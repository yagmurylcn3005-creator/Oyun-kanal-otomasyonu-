#!/usr/bin/env python3
"""Generate and save gaming video content packages, with optional unattended rotation."""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from autopilot import choose_next_topic, load_topics, mark_topic_generated
from content_automation import render_markdown
from video_workflow_core import generate_workflow_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Yerel yapay zekâ ile oyun videosu içerik paketini otomatik üretir.")
    parser.add_argument("--game", help="İsteğe bağlı oyun adı. Verilmezse konu havuzundan otomatik seçilir.")
    parser.add_argument("--platform", default=None, help="Platform; belirtilmezse otomatik konu ayarı kullanılır.")
    parser.add_argument("--style", default=None, help="Video stili; belirtilmezse otomatik konu ayarı kullanılır.")
    parser.add_argument("--tone", default=None, help="Anlatım tonu; belirtilmezse otomatik konu ayarı kullanılır.")
    parser.add_argument("--duration", type=int, default=None, help="Video süresi; belirtilmezse otomatik konu ayarı kullanılır.")
    parser.add_argument("--output-dir", default="output", help="Üretilen içeriklerin kaydedileceği klasör")
    parser.add_argument("--mode", choices=["plan", "script", "meta", "all"], default="all", help="Terminalde gösterilecek çıktı")
    parser.add_argument("--json", action="store_true", help="Terminal çıktısını JSON olarak göster")
    parser.add_argument("--no-save", action="store_true", help="Dosyaları kaydetmeden yalnızca terminal çıktısı üret")
    parser.add_argument("--watch", action="store_true", help="Sürekli çalışır; otomatik olarak yeni bir paket üretir ve bekler")
    parser.add_argument("--interval-hours", type=float, default=24, help="--watch üretimleri arasındaki saat (varsayılan: 24)")
    parser.add_argument("--topics-file", default="autopilot_topics.json", help="Otomatik konu havuzu JSON dosyası")
    parser.add_argument("--state-file", default="output/.autopilot_state.json", help="Konu rotasyon durum dosyası")
    return parser.parse_args()


def _slug(value: str) -> str:
    slug = re.sub(r"[^\w.-]+", "-", value.strip(), flags=re.UNICODE).strip("-.").lower()
    return slug or "video"


def save_package(workflow: dict, output_dir: str, game_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
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


def _select_topic(args: argparse.Namespace) -> dict:
    if args.game:
        return {
            "game": args.game,
            "platform": args.platform or "PC",
            "style": args.style or "eğlenceli ve hızlı",
            "tone": args.tone or "heyecanlı",
            "duration": args.duration or 8,
        }
    topic = choose_next_topic(load_topics(args.topics_file), args.state_file)
    for key, value in (("platform", args.platform), ("style", args.style), ("tone", args.tone), ("duration", args.duration)):
        if value is not None:
            topic[key] = value
    return topic


def run_once(args: argparse.Namespace) -> int:
    topic = _select_topic(args)
    if int(topic["duration"]) < 1:
        print("Hata: video süresi en az 1 dakika olmalı.", file=sys.stderr)
        return 2
    workflow = generate_workflow_output(
        topic["game"], topic["platform"], topic["style"], topic["tone"], int(topic["duration"])
    )
    if not args.no_save:
        destination = save_package(workflow, args.output_dir, topic["game"])
        mark_topic_generated(topic["game"], args.state_file)
        print(f"İçerik paketi kaydedildi: {destination.resolve()}", file=sys.stderr)
    generation = workflow["plan"].get("generation", {})
    if generation.get("warning"):
        print(f"Bilgi: {generation['warning']}", file=sys.stderr)
    print(_terminal_output(args, workflow))
    return 0


def main() -> int:
    load_dotenv()
    args = parse_args()
    if args.interval_hours <= 0:
        print("Hata: --interval-hours sıfırdan büyük olmalı.", file=sys.stderr)
        return 2
    if args.watch and args.no_save:
        print("Hata: --watch ile paketlerin kalıcı olması için --no-save kullanılamaz.", file=sys.stderr)
        return 2
    if not args.watch:
        return run_once(args)

    print(f"Otonom üretim açık. Her {args.interval_hours:g} saatte bir yeni paket hazırlanacak. Durdurmak için Ctrl+C.", file=sys.stderr)
    while True:
        try:
            status = run_once(args)
            if status:
                print(f"Üretim {status} koduyla tamamlanamadı; sonraki döngüde yeniden denenecek.", file=sys.stderr)
        except Exception as exc:  # unattended mode reports and continues instead of prompting
            print(f"Üretim hatası: {exc}. Sonraki döngüde tekrar denenecek.", file=sys.stderr)
        time.sleep(args.interval_hours * 3600)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nOtonom üretim durduruldu.", file=sys.stderr)
        raise SystemExit(130)
