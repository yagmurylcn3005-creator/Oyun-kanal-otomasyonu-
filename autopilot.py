"""Deterministic, local topic rotation for unattended content-package generation."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_TOPICS: list[dict[str, Any]] = [
    {"game": "Minecraft", "platform": "PC", "style": "yaratıcı ve eğlenceli", "tone": "samimi", "duration": 8},
    {"game": "Stardew Valley", "platform": "PC", "style": "sakin ve keyifli", "tone": "samimi", "duration": 8},
    {"game": "Counter-Strike 2", "platform": "PC", "style": "hızlı ve analitik", "tone": "heyecanlı", "duration": 8},
    {"game": "Fortnite", "platform": "PC", "style": "eğlenceli ve hızlı", "tone": "enerjik", "duration": 8},
    {"game": "The Witcher 3", "platform": "PC", "style": "hikâye odaklı", "tone": "sürükleyici", "duration": 10},
    {"game": "Elden Ring", "platform": "PC", "style": "analitik", "tone": "merak uyandırıcı", "duration": 10},
    {"game": "Hades", "platform": "PC", "style": "hızlı ve eğlenceli", "tone": "enerjik", "duration": 8},
    {"game": "Rocket League", "platform": "PC", "style": "rekabetçi ve eğlenceli", "tone": "heyecanlı", "duration": 8},
]


def load_topics(path: str | Path) -> list[dict[str, Any]]:
    """Load a user-editable topic list, falling back safely to built-in topics."""
    topics_path = Path(path)
    if not topics_path.exists():
        return [dict(topic) for topic in DEFAULT_TOPICS]
    try:
        data = json.loads(topics_path.read_text(encoding="utf-8"))
        topics = data.get("topics") if isinstance(data, dict) else data
        if not isinstance(topics, list):
            raise ValueError("topics must be a JSON list")
        valid = [
            {"game": str(item["game"]).strip(),
             "platform": str(item.get("platform", "PC")).strip() or "PC",
             "style": str(item.get("style", "eğlenceli ve hızlı")).strip() or "eğlenceli ve hızlı",
             "tone": str(item.get("tone", "heyecanlı")).strip() or "heyecanlı",
             "duration": int(item.get("duration", 8))}
            for item in topics
            if isinstance(item, dict) and str(item.get("game", "")).strip()
        ]
        if not valid or any(item["duration"] < 1 for item in valid):
            raise ValueError("topics must contain games with positive durations")
        return valid
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        # A broken optional config must not stop unattended generation.
        return [dict(topic) for topic in DEFAULT_TOPICS]


def choose_next_topic(topics: list[dict[str, Any]], state_path: str | Path) -> dict[str, Any]:
    """Choose the least-recently generated topic; ties follow config order."""
    if not topics:
        raise ValueError("No topics are available")
    path = Path(state_path)
    try:
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        history = state.get("last_generated", {}) if isinstance(state, dict) else {}
        if not isinstance(history, dict):
            history = {}
    except (OSError, json.JSONDecodeError):
        history = {}

    def sort_key(index_and_topic: tuple[int, dict[str, Any]]) -> tuple[str, int]:
        index, topic = index_and_topic
        last = history.get(topic["game"], "")
        return (last if isinstance(last, str) else "", index)

    return dict(min(enumerate(topics), key=sort_key)[1])


def mark_topic_generated(game: str, state_path: str | Path) -> None:
    """Persist topic rotation state atomically after package generation succeeds."""
    path = Path(state_path)
    try:
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, json.JSONDecodeError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    history = state.setdefault("last_generated", {})
    if not isinstance(history, dict):
        history = {}
        state["last_generated"] = history
    history[game] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
