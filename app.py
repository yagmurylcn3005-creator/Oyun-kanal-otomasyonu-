#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv

from content_automation import generate_content_plan, render_markdown
from video_pipeline import create_and_publish_video


def build_script_lines(game_name: str, platform: str, tone: str, style: str, duration_minutes: int) -> List[str]:
    intro = (
        f"Merhaba arkadaşlar! Bugün {game_name} oyununu {platform} üzerinde "
        f"{style} ve {tone} bir bakış açısıyla ele alıyoruz."
    )
    segments = [
        "İlk olarak oyunun genel hissini konuşalım. Görsel tasarım, menü akışı ve ilk dakikalardaki izlenim çok önemli.",
        "Sonra kontrol sistemini ve oynanış akışını inceleyelim. Bu oyun gerçekten oyuncuyu sürece bağlayabiliyor mu?",
        "Ardından oyunun güçlü ve zayıf yönlerini konuşacağız. İster eğlence odaklı bir izleyici olun, ister detaycı bir oyuncu; herkes için net bir fikir oluşturacağız.",
        "Devamında en çok dikkat çeken anları ve en çok öne çıkan mekanikleri konuşacağız. Bunlar oyunun neden izlenmeye değer olduğunu belirleyen noktalar.",
        "Son olarak da sonuç çıkaracağız: Eğer bu oyunu alırdınız? Hangi tür oyuncular için daha uygun?",
    ]
    closing = (
        f"Kısacası, {game_name} oyununu {platform} üzerinde oynarken ne hissettiniz? Yorumlarda "
        "düşüncelerinizi yazın, bir sonraki videoda başka bir oyunu birlikte inceleyelim!"
    )
    return [intro, *segments, closing]


def build_youtube_metadata(game_name: str, platform: str, style: str, duration_minutes: int) -> Dict[str, Any]:
    title = f"{game_name} {platform} İncelemesi | {duration_minutes} Dakika {style} Oynanış"
    description = (
        f"{game_name} oyununun {platform} sürümünü deneyimledik. "
        f"Oynanış, grafikler, hikâye, zorluk seviyeleri ve genel öneri hakkındaki düşüncelerimizi paylaşıyoruz. "
        f"Bu video {style} bir anlatımla hazırlanmıştır."
    )
    tags = [
        game_name,
        platform,
        "oyun incelemesi",
        style,
        "youtube oyun videosu",
        "oyun analizi",
        "pc oyun",
    ]
    return {
        "title": title,
        "description": description,
        "tags": tags,
    }


def generate_workflow_output(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: str | None = None,
) -> Dict[str, Any]:
    plan = generate_content_plan(
        game_name=game_name,
        platform=platform,
        style=style,
        tone=tone,
        duration_minutes=duration_minutes,
        api_key=api_key,
    )

    script_lines = build_script_lines(game_name, platform, tone, style, duration_minutes)
    meta = build_youtube_metadata(game_name, platform, style, duration_minutes)

    script_text = "\n\n".join(f"{idx}. {line}" for idx, line in enumerate(script_lines, start=1))
    youtube_meta_text = (
        f"Title: {meta['title']}\n\n"
        f"Description:\n{meta['description']}\n\n"
        f"Tags: {', '.join(meta['tags'])}"
    )

    return {
        "plan": plan,
        "script_lines": script_lines,
        "script_text": script_text,
        "youtube_meta": meta,
        "youtube_meta_text": youtube_meta_text,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YouTube oyun kanalı için yapay zeka içerik otomasyonu."
    )
    parser.add_argument("--game", required=True, help="Oyun adı, örn. CS2, Zelda, Fortnite")
    parser.add_argument("--platform", default="PC", help="Platform, örn. PC, PS5, Xbox")
    parser.add_argument(
        "--style",
        default="eğlenceli ve hızlı",
        help="İçerik tonu / video stili",
    )
    parser.add_argument(
        "--tone",
        default="heyecanlı",
        help="Ses tonu, örn. eğlenceli, analitik, merak uyandırıcı",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=8,
        help="Video süresi (dakika)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Çıktı formatı",
    )
    parser.add_argument(
        "--mode",
        choices=["plan", "script", "meta", "all", "publish"],
        default="all",
        help="Üretilecek içerik tipi",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Video oluşturup YouTube'a yüklemeyi dener.",
    )
    parser.add_argument(
        "--client-secrets",
        default=None,
        help="YouTube upload için client_secret.json yolu.",
    )
    parser.add_argument(
        "--credentials-path",
        default=None,
        help="Google kimlik doğrulama dosyası yolu.",
    )
    parser.add_argument(
        "--privacy-status",
        choices=["public", "private", "unlisted"],
        default="private",
        help="YouTube yayın durumunu belirler.",
    )
    parser.add_argument(
        "--output-dir",
        default="output/videos",
        help="Video dosyalarının kaydedileceği klasör.",
    )
    return parser.parse_args()


def build_output(mode: str, game: str, platform: str, style: str, tone: str, duration: int, api_key: str | None) -> str:
    workflow = generate_workflow_output(
        game_name=game,
        platform=platform,
        style=style,
        tone=tone,
        duration_minutes=duration,
        api_key=api_key,
    )

    if mode == "plan":
        return render_markdown(workflow["plan"])

    if mode == "script":
        return workflow["script_text"]

    if mode == "meta":
        return workflow["youtube_meta_text"]

    if mode == "publish":
        return workflow["youtube_meta_text"]

    return (
        render_markdown(workflow["plan"]) + "\n\n---\n\n" + workflow["script_text"] + "\n\n---\n\n" + workflow["youtube_meta_text"]
    )


def main() -> int:
    load_dotenv()
    args = parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")

    if args.publish:
        try:
            result = create_and_publish_video(
                game_name=args.game,
                platform=args.platform,
                style=args.style,
                tone=args.tone,
                duration_minutes=args.duration,
                api_key=api_key,
                client_secrets_path=args.client_secrets,
                credentials_path=args.credentials_path,
                privacy_status=args.privacy_status,
                output_dir=args.output_dir,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except Exception as exc:  # pragma: no cover - runtime upload fails if env or deps missing
            print(f"Yayın işlemi başarısız: {exc}", file=sys.stderr)
            return 1

    output = build_output(
        mode=args.mode,
        game=args.game,
        platform=args.platform,
        style=args.style,
        tone=args.tone,
        duration=args.duration,
        api_key=api_key,
    )

    if args.output == "json":
        workflow = generate_workflow_output(
            game_name=args.game,
            platform=args.platform,
            style=args.style,
            tone=args.tone,
            duration_minutes=args.duration,
            api_key=api_key,
        )
        print(json.dumps(workflow, ensure_ascii=False, indent=2))
        return 0

    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nİşlem kullanıcı tarafından iptal edildi.", file=sys.stderr)
        raise SystemExit(130)


__all__ = [
    "build_script_lines",
    "build_youtube_metadata",
    "generate_workflow_output",
    "build_output",
    "create_and_publish_video",
]


