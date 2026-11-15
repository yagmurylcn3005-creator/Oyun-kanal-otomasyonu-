import json
import re
from typing import Any, Dict, Iterable, List


def _normalize_list(value: Any, fallback: Iterable[str] | None = None) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return list(fallback or [])
    return [str(value)]


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
        "cta": "Bu videoyu beğendiyseniz yorumlarda hangi oyunu bir sonraki videoda görmek istediğinizi yazın!",
        "seo_tags": [game_name, platform, style, "oyun incelemesi", "youtube oyun videosu"],
    }


def _extract_json_payload(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Boş model yanıtı.")

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("Model JSON olarak değil, farklı format döndürdü.")
    return payload


def _merge_plan_defaults(plan: Dict[str, Any], *, platform: str, style: str, tone: str, duration_minutes: int) -> Dict[str, Any]:
    merged = dict(plan or {})
    merged.setdefault("platform", platform)
    merged.setdefault("style", style)
    merged.setdefault("tone", tone)
    merged.setdefault("duration_minutes", duration_minutes)
    merged.setdefault("title", f"{platform} platformunda {style} {duration_minutes} dakikalık video")
    merged.setdefault("hook", "Oyun hakkında güçlü bir açılış hazırlıyoruz.")
    merged.setdefault("summary", "Bu video için net bir hikâye akışı oluşturuluyor.")
    merged.setdefault("outline", ["Giriş", "Oynanış", "Değerlendirme"])
    merged.setdefault("shot_list", ["Açılış", "Oynanış", "Sonuç"])
    merged.setdefault("cta", "Abone olun ve sonraki videoda devam edelim.")
    merged.setdefault("seo_tags", [platform, style, "oyun incelemesi"])
    merged["outline"] = _normalize_list(merged.get("outline"), ["Giriş", "Oynanış", "Değerlendirme"])
    merged["shot_list"] = _normalize_list(merged.get("shot_list"), ["Açılış", "Oynanış", "Sonuç"])
    merged["seo_tags"] = _normalize_list(merged.get("seo_tags"), [platform, style, "oyun incelemesi"])
    return merged


def generate_content_plan(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: str | None = None,
) -> Dict[str, Any]:
    plan = build_local_plan(game_name, platform, style, tone, duration_minutes)

    if not api_key:
        return plan

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw_text = getattr(response, "text", None) or str(response)
        payload = _extract_json_payload(raw_text)
        return _merge_plan_defaults(payload, platform=platform, style=style, tone=tone, duration_minutes=duration_minutes)
    except Exception:
        return plan


def render_markdown(plan: Dict[str, Any]) -> str:
    safe_plan = plan or {}
    outline = "\n".join(f"{index}. {item}" for index, item in enumerate(_normalize_list(safe_plan.get("outline"), ["Giriş", "Oynanış", "Değerlendirme"]), start=1))
    shot_list = "\n".join(f"- {item}" for item in _normalize_list(safe_plan.get("shot_list"), ["Açılış", "Oynanış", "Sonuç"]))
    seo_tags = ", ".join(_normalize_list(safe_plan.get("seo_tags"), ["oyun", "inceleme"]))

    return f"""# {safe_plan.get('title', 'Oyun İçerik Planı')}

## Açılış cümlesi
{safe_plan.get('hook', 'Oyun hakkında güçlü bir giriş hazırlıyoruz.')}

## Özet
{safe_plan.get('summary', 'Bu video için net bir hikâye akışı oluşturuluyor.')}

## Video akışı
{outline}

## Görüntü planı
{shot_list}

## CTA
{safe_plan.get('cta', 'Abone olun ve sonraki videoda devam edelim.')}

## SEO etiketleri
{seo_tags}
"""


__all__ = ["build_local_plan", "generate_content_plan", "render_markdown"]












































































































































































































































































