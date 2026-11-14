from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from config import DEFAULT_DURATION, DEFAULT_PLATFORM, DEFAULT_STYLE, DEFAULT_TONE


def build_local_plan(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
) -> Dict[str, Any]:
    title = f"{game_name} {platform} ile {duration_minutes} dakikalık {style} incelemesi"
    hook = (
        f"Bugün {game_name} oyununu {platform} üzerinde inceleyeceğiz; "
        "görünüşe göre herkesin konuştuğu bu oyun gerçekten beklediği kadar iyi mi?"
    )

    outline = [
        "Oyun fikri ve görsel estetiği",
        "İlk izlenim ve kontrol deneyimi",
        "Oyuncu ilerleyişi ve içerik derinliği",
        "Görsel ve ses kalitesi",
        "Sonuç: İzlenmeye değer mi?",
    ]

    shot_list = [
        "Açılış sahnesi ve kısa açıklama",
        "Oyun menüsü ve genel görünüm",
        "Ana oynanışın ilk dakikaları",
        "Öne çıkan mekanikler ve zorluklar",
        "Son karar ve öneri",
    ]

    thumbnail_prompt = (
        f"Yüksek kontrastlı, dikkat çeken, {game_name} için oyun inceleme kapağı. "
        f"{platform} platformu, {style} ton, {tone} his, dikkat çekici başlık, canlı ışıklar, "
        "oyun ekran görüntüsü ve karakterler, YouTube thumbnail tasarımı."
    )

    return {
        "title": title,
        "hook": hook,
        "platform": platform,
        "style": style,
        "tone": tone,
        "duration_minutes": duration_minutes,
        "summary": (
            f"{game_name} için {style} bir içerik üretimi planı. "
            "İzleyicinin dikkatini çekmek için güçlü bir açılış, kısa hikâye akışı, "
            "oyunun güçlü yönlerini vurgulayan sahneler ve net bir sonuç sunulur."
        ),
        "outline": outline,
        "shot_list": shot_list,
        "thumbnail_prompt": thumbnail_prompt,
        "audience": "oyun severler",
        "format": "youtube",
        "cta": "Bu videoyu beğendiyseniz yorumlarda hangi oyunu bir sonraki videoda görmek istediğinizi yazın!",
        "seo_tags": [game_name, platform, style, "oyun incelemesi", "youtube oyun videosu"],
    }


def _extract_json_payload(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Boş model yanıtı.")

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    return json.loads(text)


def generate_content_plan(
    game_name: str,
    platform: str = DEFAULT_PLATFORM,
    style: str = DEFAULT_STYLE,
    tone: str = DEFAULT_TONE,
    duration_minutes: int = DEFAULT_DURATION,
    api_key: str | None = None,
) -> Dict[str, Any]:
    plan = build_local_plan(game_name, platform, style, tone, duration_minutes)

    if not api_key:
        return plan

    try:
        from services.ai_client import generate_structured_response

        prompt = f"""
        Aşağıdaki bilgileri kullanarak YouTube oyun videosu için kısa ama profesyonel bir içerik planı üret.
        Output sadece JSON olmalı. Format:
        {{
          "title": "...",
          "hook": "...",
          "summary": "...",
          "outline": ["...","..."],
          "shot_list": ["...","..."],
          "cta": "...",
          "seo_tags": ["...","..."]
        }}

        Oyun: {game_name}
        Platform: {platform}
        Stil: {style}
        Ton: {tone}
        Video süresi: {duration_minutes} dakika
        """

        payload = generate_structured_response(prompt, api_key)
        if not isinstance(payload, dict):
            raise ValueError("Model JSON olarak değil, farklı format döndürdü.")

        payload.setdefault("platform", platform)
        payload.setdefault("style", style)
        payload.setdefault("tone", tone)
        payload.setdefault("duration_minutes", duration_minutes)
        payload.setdefault("thumbnail_prompt", plan["thumbnail_prompt"])
        payload.setdefault("audience", "oyun severler")
        payload.setdefault("format", "youtube")
        return payload
    except Exception:
        return plan


def render_markdown(plan: Dict[str, Any]) -> str:
    outline = "\n".join(f"{index}. {item}" for index, item in enumerate(plan.get("outline", []), start=1))
    shot_list = "\n".join(f"- {item}" for item in plan.get("shot_list", []))
    seo_tags = ", ".join(plan.get("seo_tags", []))
    thumbnail = plan.get("thumbnail_prompt", "")

    return f"""# {plan.get('title', 'Oyun İçerik Planı')}

## Açılış cümlesi
{plan.get('hook', 'Oyun hakkında güçlü bir giriş hazırlıyoruz.')}

## Özet
{plan.get('summary', 'Bu video için net bir hikâye akışı oluşturuluyor.')}

## Video akışı
{outline}

## Görüntü planı
{shot_list}

## CTA
{plan.get('cta', 'Abone olun ve sonraki videoda devam edelim.')}

## Thumbnail önerisi
{thumbnail or 'Yüksek kontrastlı game thumbnail tasarımı.'}

## SEO etiketleri
{seo_tags}
"""


def build_script_lines(
    game_name: str,
    platform: str,
    tone: str,
    style: str,
    duration_minutes: int,
) -> List[str]:
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


def build_youtube_metadata(
    game_name: str,
    platform: str,
    style: str,
    duration_minutes: int,
) -> Dict[str, Any]:
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


def build_thumbnail_prompt(game_name: str, platform: str, style: str, tone: str) -> str:
    return (
        f"YouTube oyun inceleme thumbnail tasarımı. {game_name} oyunu, {platform} platformu, "
        f"{style} anlatım, {tone} ruh hali, parlak ışıklar, yüksek kontrast, net başlık, "
        "düşünceli ve dikkat çekici bir kompozisyon."
    )


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
    thumbnail_prompt = build_thumbnail_prompt(game_name, platform, style, tone)

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
        "thumbnail_prompt": thumbnail_prompt,
    }


def build_output(
    mode: str,
    game: str,
    platform: str,
    style: str,
    tone: str,
    duration: int,
    api_key: str | None,
) -> str:
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

    if mode == "thumbnail":
        return workflow["thumbnail_prompt"]

    return (
        render_markdown(workflow["plan"]) + "\n\n---\n\n" + workflow["script_text"] + "\n\n---\n\n" + workflow["youtube_meta_text"]
    )
