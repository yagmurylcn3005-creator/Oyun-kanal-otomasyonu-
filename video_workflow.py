#!/usr/bin/env python3
"""Generate and save a complete, ready-to-produce gaming video content package."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from content_automation import render_markdown
from video_workflow_core import generate_workflow_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Yerel yapay zekâ ile oyun videosu içerik paketini üretip dosyalara kaydeder.")
    parser.add_argument("--game", required=True, help="Oyun adı, örn. CS2, Zelda, Fortnite")
    parser.add_argument("--platform", default="PC", help="Platform: PC, PS5, Xbox, Switch vb.")
    parser.add_argument("--style", default="eğlenceli ve hızlı", help="Video stili")
    parser.add_argument("--tone", default="heyecanlı", help="Anlatım tonu")
    parser.add_argument("--duration", type=int, default=8, help="Video süresi (dakika)")
    parser.add_argument("--output-dir", default="output", help="Üretilen içeriklerin kaydedileceği klasör")
    parser.add_argument("--mode", choices=["plan", "script", "meta", "all"], default="all", help="Terminalde gösterilecek çıktı")
    parser.add_argument("--json", action="store_true", help="Terminal çıktısını JSON olarak göster")
    parser.add_argument("--no-save", action="store_true", help="Dosyaları kaydetmeden yalnızca terminal çıktısı üret")
    return parser.parse_args()


def _slug(value: str) -> str:
    slug = re.sub(r"[^\w.-]+", "-", value.strip(), flags=re.UNICODE).strip("-.").lower()
    return slug or "video"


def save_package(workflow: dict, output_dir: str, game_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = Path(output_dir) / f"{_slug(game_name)}-{timestamp}"
    target.mkdir(parents=True, exist_ok=False)
    plan = workflow["plan"]
    (target / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target / "summary.md").write_text(render_markdown(plan), encoding="utf-8")
    (target / "script.txt").write_text(workflow["script_text"].rstrip() + "\n", encoding="utf-8")
    (target / "youtube_meta.txt").write_text(workflow["youtube_meta_text"].rstrip() + "\n", encoding="utf-8")
    (target / "youtube_meta.json").write_text(json.dumps(workflow["youtube_meta"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def _terminal_output(args: argparse.Namespace, workflow: dict) -> str:
    if args.json:
        return json.dumps(workflow, ensure_ascii=False, indent=2)
    if args.mode == "plan":
        return render_markdown(workflow["plan"])
    if args.mode == "script":
        return workflow["script_text"]
    if args.mode == "meta":
        return workflow["youtube_meta_text"]
    return render_markdown(workflow["plan"]) + "\n---\n\n" + workflow["script_text"] + "\n---\n\n" + workflow["youtube_meta_text"]


def main() -> int:
    load_dotenv()
    args = parse_args()
    if args.duration < 1:
        print("Hata: --duration en az 1 olmalı.", file=sys.stderr)
        return 2
    workflow = generate_workflow_output(args.game, args.platform, args.style, args.tone, args.duration)
    if not args.no_save:
        destination = save_package(workflow, args.output_dir, args.game)
        print(f"İçerik paketi kaydedildi: {destination.resolve()}", file=sys.stderr)
    generation = workflow["plan"].get("generation", {})
    if generation.get("warning"):
        print(f"Bilgi: {generation['warning']}", file=sys.stderr)
        print("Yerel AI için Ollama'yı başlatın ve modelin indirildiğini kontrol edin.", file=sys.stderr)
    print(_terminal_output(args, workflow))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nİşlem kullanıcı tarafından iptal edildi.", file=sys.stderr)
        raise SystemExit(130)
