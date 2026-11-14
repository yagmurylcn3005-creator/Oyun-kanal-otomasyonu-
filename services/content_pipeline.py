#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config import ALLOWED_MODES, DEFAULT_DURATION, DEFAULT_GAME, DEFAULT_PLATFORM, DEFAULT_STYLE, DEFAULT_TONE, VALID_OUTPUT_FORMATS, ensure_output_dir, get_google_api_key
from services.content_pipeline import build_output, generate_workflow_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YouTube oyun kanalı için yapay zeka içerik otomasyonu."
    )
    parser.add_argument("--game", default=DEFAULT_GAME, help="Oyun adı, örn. CS2, Zelda, Fortnite")
    parser.add_argument("--platform", default=DEFAULT_PLATFORM, help="Platform, örn. PC, PS5, Xbox")
    parser.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        help="İçerik tonu / video stili",
    )
    parser.add_argument(
        "--tone",
        default=DEFAULT_TONE,
        help="Ses tonu, örn. eğlenceli, analitik, merak uyandırıcı",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help="Video süresi (dakika)",
    )
    parser.add_argument(
        "--output",
        choices=list(VALID_OUTPUT_FORMATS),
        default="text",
        help="Çıktı formatı",
    )
    parser.add_argument(
        "--mode",
        choices=list(ALLOWED_MODES),
        default="all",
        help="Üretilecek içerik tipi",
    )
    parser.add_argument(
        "--save",
        default=None,
        help="Sonucu kaydetmek için dosya yolu. Örn. output/video.txt",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = get_google_api_key()

    if args.output == "json":
        workflow = generate_workflow_output(
            game_name=args.game,
            platform=args.platform,
            style=args.style,
            tone=args.tone,
            duration_minutes=args.duration,
            api_key=api_key,
        )
        rendered = json.dumps(workflow, ensure_ascii=False, indent=2)
        if args.save:
            path = Path(args.save)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
        print(rendered)
        return 0

    output = build_output(
        mode=args.mode,
        game=args.game,
        platform=args.platform,
        style=args.style,
        tone=args.tone,
        duration=args.duration,
        api_key=api_key,
    )

    if args.save:
        path = Path(args.save)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nİşlem kullanıcı tarafından iptal edildi.", file=sys.stderr)
        raise SystemExit(130)
