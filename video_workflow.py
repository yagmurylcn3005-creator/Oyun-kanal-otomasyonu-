from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from video_workflow import generate_workflow_output


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "video"


def build_video_project(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: Optional[str] = None,
    output_dir: Optional[str | Path] = None,
) -> Dict[str, Any]:
    workflow = generate_workflow_output(
        game_name=game_name,
        platform=platform,
        style=style,
        tone=tone,
        duration_minutes=duration_minutes,
        api_key=api_key,
    )

    safe_dir = Path(output_dir) if output_dir else Path("output") / "videos"
    project_dir = safe_dir / _slugify(game_name)
    project_dir.mkdir(parents=True, exist_ok=True)

    base_name = _slugify(f"{game_name}-{platform}")
    project = {
        "game_name": game_name,
        "platform": platform,
        "style": style,
        "tone": tone,
        "duration_minutes": duration_minutes,
        "workflow": workflow,
        "title": workflow["youtube_meta"]["title"],
        "description": workflow["youtube_meta"]["description"],
        "tags": workflow["youtube_meta"]["tags"],
        "script_lines": workflow["script_lines"],
        "script_text": workflow["script_text"],
        "project_dir": str(project_dir),
        "thumbnail_path": str(project_dir / f"{base_name}-thumbnail.png"),
        "video_path": str(project_dir / f"{base_name}.mp4"),
        "audio_path": str(project_dir / f"{base_name}.mp3"),
    }
    return project


def _make_title_card(title: str, subtitle: str, output_path: str, accent: str = "#E11D48") -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover - depends on runtime dependencies
        raise RuntimeError("Pillow is required to render video thumbnails. Install requirements.txt") from exc

    width, height = 1920, 1080
    image = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        alpha = y / height
        color = (int(15 + 20 * alpha), int(23 + 20 * alpha), int(42 + 20 * alpha))
        draw.line((0, y, width, y), fill=color)

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 72)
        subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except OSError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) / 2
    title_y = 250
    draw.rounded_rectangle((title_x - 40, title_y - 20, title_x + title_width + 40, title_y + 110), radius=24, fill=accent)
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))

    subtitle_x = 200
    subtitle_y = 600
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(214, 227, 255))

    image.save(output_path)
    return output_path


def _generate_tts_audio(script_text: str, output_path: str) -> str | None:
    try:
        from gtts import gTTS
    except ImportError:
        return None

    try:
        tts = gTTS(text=script_text, lang="tr", slow=False)
        tts.save(output_path)
        return output_path
    except Exception:
        return None


def render_video(project: Dict[str, Any], output_dir: Optional[str | Path] = None) -> Dict[str, Any]:
    target_dir = Path(output_dir) if output_dir else Path(project["project_dir"])
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
        import numpy as np
    except ImportError as exc:  # pragma: no cover - depends on runtime dependencies
        raise RuntimeError("moviepy and numpy are required to render MP4. Install requirements.txt") from exc

    title_card_path = _make_title_card(project["title"], project["platform"], project["thumbnail_path"])
    title_image = ImageClip(str(title_card_path), duration=5)
    clips = [title_image]

    for idx, line in enumerate(project["script_lines"], start=1):
        frame_path = _make_title_card(f"Bölüm {idx}", line[:90], str(target_dir / f"scene_{idx}.png"), accent="#8B5CF6")
        clip = ImageClip(str(frame_path), duration=max(3, min(6, 2 + len(line) / 40)))
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    audio_path = project["audio_path"]
    _generate_tts_audio(project["script_text"], audio_path)
    if os.path.exists(audio_path):
        video = video.with_audio(AudioFileClip(audio_path))

    out_path = project["video_path"]
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile=str(target_dir / "temp_audio.wav"))
    project["rendered_video_path"] = out_path
    project["thumbnail_path"] = title_card_path
    return project


def build_youtube_upload_body(
    title: str,
    description: str,
    tags: List[str],
    privacy_status: str = "private",
    category_id: str = "20",
) -> Dict[str, Any]:
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }


def _get_youtube_credentials(client_secrets_path: str | None = None, credentials_path: str | None = None):
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:  # pragma: no cover - depends on runtime dependencies
        raise RuntimeError("google-auth-oauthlib and google-auth are required for YouTube upload. Install requirements.txt") from exc

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    secrets_path = client_secrets_path or os.getenv("YOUTUBE_CLIENT_SECRETS")
    if not secrets_path:
        raise ValueError("YOUTUBE_CLIENT_SECRETS or --client-secrets is required for upload.")

    creds_file = credentials_path or os.getenv("YOUTUBE_CREDENTIALS_PATH", "youtube_credentials.json")
    if os.path.exists(creds_file):
        return Credentials.from_authorized_user_file(creds_file, scopes)

    flow = InstalledAppFlow.from_client_secrets_file(secrets_path, scopes)
    creds = flow.run_local_server(port=0)
    with open(creds_file, "w", encoding="utf-8") as handle:
        json.dump({
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }, handle)
    return creds


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    client_secrets_path: str | None = None,
    credentials_path: str | None = None,
    privacy_status: str = "private",
    category_id: str = "20",
) -> Dict[str, Any]:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:  # pragma: no cover - depends on runtime dependencies
        raise RuntimeError("google-api-python-client is required for YouTube upload. Install requirements.txt") from exc

    credentials = _get_youtube_credentials(client_secrets_path=client_secrets_path, credentials_path=credentials_path)
    youtube = build("youtube", "v3", credentials=credentials)
    body = build_youtube_upload_body(title=title, description=description, tags=tags, privacy_status=privacy_status, category_id=category_id)

    media = MediaFileUpload(video_path, resumable=True, chunksize=-1, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response


def create_and_publish_video(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: Optional[str] = None,
    client_secrets_path: Optional[str] = None,
    credentials_path: Optional[str] = None,
    privacy_status: str = "private",
    category_id: str = "20",
    output_dir: Optional[str | Path] = None,
) -> Dict[str, Any]:
    project = build_video_project(
        game_name=game_name,
        platform=platform,
        style=style,
        tone=tone,
        duration_minutes=duration_minutes,
        api_key=api_key,
        output_dir=output_dir,
    )
    project = render_video(project, output_dir=output_dir)
    result = upload_to_youtube(
        video_path=project["video_path"],
        title=project["title"],
        description=project["description"],
        tags=project["tags"],
        client_secrets_path=client_secrets_path,
        credentials_path=credentials_path,
        privacy_status=privacy_status,
        category_id=category_id,
    )
    return {
        "project": project,
        "youtube_upload": result,
    }


__all__ = [
    "build_video_project",
    "render_video",
    "build_youtube_upload_body",
    "upload_to_youtube",
    "create_and_publish_video",
]


if __name__ == "__main__":
    sample = build_video_project("CS2", "PC", "eğlenceli ve hızlı", "heyecanlı", 8)
    print(json.dumps(sample["workflow"]["youtube_meta"], ensure_ascii=False, indent=2))
