from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class GameBrief:
    game_name: str
    platform: str
    style: str
    tone: str
    duration_minutes: int


@dataclass
class ContentPlan:
    title: str
    hook: str
    summary: str
    outline: List[str]
    shot_list: List[str]
    cta: str
    seo_tags: List[str]
    thumbnail_prompt: str = ""
    audience: str = "oyun severler"
    format: str = "youtube"
    platform: str = "PC"
    style: str = "eğlenceli ve hızlı"
    tone: str = "heyecanlı"
    duration_minutes: int = 8

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class YoutubeMetadata:
    title: str
    description: str
    tags: List[str]
    thumbnail_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowOutput:
    plan: Dict[str, Any]
    script_lines: List[str]
    script_text: str
    youtube_meta: Dict[str, Any]
    youtube_meta_text: str
    thumbnail_prompt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
