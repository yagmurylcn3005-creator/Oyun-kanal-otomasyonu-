from __future__ import annotations

import re
from typing import Any, Dict, List

from content_automation import generate_content_plan


def build_script_lines(game_name: str, platform: str, tone: str, style: str, duration_minutes: int) -> List[str]:
    plan = generate_content_plan(game_name, platform, style, tone, duration_minutes)
    return [part for part in plan.get("script", "").split("\n\n") if part.strip()]


def build_youtube_metadata(game_name: str, platform: str, style: str, duration_minutes: int, plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
    plan = plan or {}
    title = plan.get("title") or f"{game_name} {platform} İncelemesi | {duration_minutes} Dakikada {style}"
    description = (
        f"{game_name} oyununu {platform} üzerinde inceliyoruz. "
        f"Bu {style} videoda oynanış, dikkat çeken noktalar ve genel değerlendirmeyi bulabilirsiniz.\n\n"
        "⚠️ Video, içerik üreticisinin kendi oynanış görüntüleri ve deneyimiyle tamamlanmalıdır.\n\n"
        "Siz ne düşünüyorsunuz? Yorumlarda paylaşın; sonraki video önerinizi yazın!"
    )
    tags = plan.get("seo_tags") or [game_name, platform, "oyun incelemesi", style, "Türkçe oyun", "oyun videosu"]
    return {"title": title, "description": description, "tags": tags, "hashtags": ["#oyun", "#oyunincelemesi", "#gaming"]}


def generate_workflow_output(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: str | None = None,
) -> Dict[str, Any]:
    plan = generate_content_plan(game_name, platform, style, tone, duration_minutes, api_key=api_key)
    script_text = plan.get("script") or "\n\n".join(build_script_lines(game_name, platform, tone, style, duration_minutes))
    script_lines = [part for part in re.split(r"\n\s*\n", script_text) if part.strip()]
    metadata = build_youtube_metadata(game_name, platform, style, duration_minutes, plan)
    metadata_text = (
        f"Başlık: {metadata['title']}\n\nAçıklama:\n{metadata['description']}\n\n"
        f"Etiketler: {', '.join(metadata['tags'])}\n\nHashtagler: {' '.join(metadata['hashtags'])}"
    )
    return {
        "plan": plan,
        "script_lines": script_lines,
        "script_text": script_text,
        "youtube_meta": metadata,
        "youtube_meta_text": metadata_text,
    }


__all__ = ["build_script_lines", "build_youtube_metadata", "generate_workflow_output"]
