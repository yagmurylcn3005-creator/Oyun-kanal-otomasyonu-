import json
import os
import re
from typing import Any, Dict

import requests


def build_local_plan(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
) -> Dict[str, Any]:
    """Build a useful offline fallback when Ollama is unavailable."""
    outline = [
        "Açılış ve oyunun kısa tanıtımı",
        "İlk izlenim, kontroller ve temel oynanış",
        "Öne çıkan mekanikler ve içerik derinliği",
        "Güçlü yönler, geliştirilmesi gereken noktalar ve görüntü önerileri",
        "Kimlere önerilir? Son karar ve izleyiciye soru",
    ]
    shot_list = [
        "Oyunun dikkat çekici bir anıyla soğuk açılış",
        "Oyun adı, platform ve kısa bağlam",
        "Temel oynanışı gösteren kesintisiz görüntüler",
        "Öne çıkan mekaniklerden örnekler; yorumla görüntüyü eşleştir",
        "Son değerlendirme ve kapanış ekranı",
    ]
    script = "\n\n".join(
        [
            f"[AÇILIŞ]\nMerhaba arkadaşlar! Bugün {game_name} oyununa {platform} üzerinde, {style} ve {tone} bir göz atıyoruz. İlk sorumuz şu: Bu oyun gerçekten zaman ayırmaya değer mi?",
            f"[İLK İZLENİM]\nÖnce oyunun dünyasına ve ilk dakikalardaki hissine bakalım. Görüntülerde menüden oyuna geçişi ve ilk karşılaşmayı gösterin. Kontrollerin ne kadar anlaşılır olduğunu kendi deneyiminizle anlatın.",
            f"[OYNANIŞ]\nŞimdi {game_name} oyununu farklı kılan mekanikleri inceleyelim. Bu bölümde kendi oynanış kaydınızdan örnekler ekleyin; güçlü yanları ve sizi zorlayan noktaları somut örneklerle açıklayın.",
            "[DEĞERLENDİRME]\nGörsel ve ses tasarımının deneyime katkısını, içerik çeşitliliğini ve oyunun kimlere hitap edebileceğini değerlendirin. Bilmediğiniz veya test etmediğiniz özellikler hakkında kesin iddialarda bulunmayın.",
            f"[KAPANIŞ]\nGenel olarak {game_name}, özellikle bu türü seven oyuncuların ilgisini çekebilir. Siz oyunu oynadınız mı; sıradaki videoda hangi oyunu inceleyelim? Yorumlarda buluşalım, görüşmek üzere!",
        ]
    )
    return {
        "title": f"{game_name} {platform} İncelemesi | {duration_minutes} Dakikada {style}",
        "hook": f"{game_name} gerçekten zaman ayırmaya değer mi? {platform} üzerinde birlikte bakalım.",
        "platform": platform,
        "style": style,
        "tone": tone,
        "duration_minutes": duration_minutes,
        "summary": f"{game_name} için {style} ve {tone} anlatımlı, yaklaşık {duration_minutes} dakikalık oyun videosu taslağı.",
        "outline": outline,
        "shot_list": shot_list,
        "script": script,
        "cta": "Videoyu beğendiyseniz beğenmeyi ve abone olmayı unutmayın. Bir sonraki oyunu yorumlarda önerin!",
        "seo_tags": [game_name, platform, style, "oyun incelemesi", "oyun videosu", "Türkçe oyun"],
        "generation": {"provider": "offline-template", "model": None},
    }


def _extract_json_payload(text: str) -> Dict[str, Any]:
    """Parse a JSON object, tolerating a model's optional Markdown fences."""
    if not text or not text.strip():
        raise ValueError("Yerel model boş yanıt verdi.")
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        payload = json.loads(cleaned[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("Yerel model JSON nesnesi döndürmedi.")
    return payload


def _call_ollama(prompt: str) -> Dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.7, "num_predict": 4096},
        },
        timeout=(5, int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))),
    )
    response.raise_for_status()
    data = response.json()
    return _extract_json_payload(data.get("response", ""))


def _prompt_for_video(game_name: str, platform: str, style: str, tone: str, duration_minutes: int) -> str:
    schema = {
        "title": "YouTube başlığı",
        "hook": "İlk 10 saniyelik açılış cümlesi",
        "summary": "Video özeti",
        "outline": ["dakika aralıklarıyla video bölümleri"],
        "shot_list": ["çekilecek oyun görüntüleri"],
        "script": "Türkçe, seslendirilebilir tam video metni; bölüm başlıkları kullan",
        "cta": "izleyiciye çağrı",
        "seo_tags": ["etiket"],
    }
    return (
        "Sen Türkçe içerik hazırlayan bir oyun kanalı editörüsün. Video için aşağıdaki JSON şemasında "
        "yalnızca geçerli JSON üret. Süreye uygun, doğal ve özgün bir anlatım yaz. Oyunun doğrulanmamış "
        "özelliklerini uydurma; içerik üreticisinin kendi oynanış görüntüsü/deneyimi eklemesi gereken yerleri "
        "[KENDİ DENEYİMİNİ EKLE] diye belirt. Script Türkçe olsun.\n"
        f"Şema: {json.dumps(schema, ensure_ascii=False)}\n"
        f"Oyun: {game_name}\nPlatform: {platform}\nStil: {style}\nTon: {tone}\nSüre: {duration_minutes} dakika"
    )


def generate_content_plan(
    game_name: str,
    platform: str,
    style: str,
    tone: str,
    duration_minutes: int,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Generate with local Ollama; fall back to an offline template, never a cloud API.

    ``api_key`` remains accepted for compatibility with older callers but is intentionally unused.
    Set USE_LOCAL_LLM=false to explicitly use the offline template without contacting Ollama.
    """
    if not game_name.strip():
        raise ValueError("Oyun adı boş bırakılamaz.")
    if duration_minutes < 1:
        raise ValueError("Video süresi en az 1 dakika olmalı.")

    fallback = build_local_plan(game_name, platform, style, tone, duration_minutes)
    if os.getenv("USE_LOCAL_LLM", "true").strip().lower() not in {"1", "true", "yes", "on"}:
        return fallback

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    try:
        generated = _call_ollama(_prompt_for_video(game_name, platform, style, tone, duration_minutes))
        # Preserve safe defaults for missing/invalid model fields.
        for key in ("title", "hook", "summary", "script", "cta"):
            if not isinstance(generated.get(key), str) or not generated[key].strip():
                generated[key] = fallback[key]
        for key in ("outline", "shot_list", "seo_tags"):
            if not isinstance(generated.get(key), list) or not all(isinstance(item, str) for item in generated[key]):
                generated[key] = fallback[key]
        generated.update(
            platform=platform,
            style=style,
            tone=tone,
            duration_minutes=duration_minutes,
            generation={"provider": "ollama", "model": model},
        )
        return generated
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        fallback["generation"] = {
            "provider": "offline-template",
            "model": None,
            "warning": f"Ollama kullanılamadı; şablon kullanıldı: {exc}",
        }
        return fallback


def render_markdown(plan: Dict[str, Any]) -> str:
    outline = "\n".join(f"{index}. {item}" for index, item in enumerate(plan.get("outline", []), start=1))
    shot_list = "\n".join(f"- {item}" for item in plan.get("shot_list", []))
    tags = ", ".join(plan.get("seo_tags", []))
    generation = plan.get("generation", {})
    source = generation.get("provider", "unknown")
    return f"""# {plan.get('title', 'Oyun İçerik Planı')}

> Üretim kaynağı: {source}

## Açılış cümlesi
{plan.get('hook', '')}

## Özet
{plan.get('summary', '')}

## Video akışı
{outline}

## Görüntü planı
{shot_list}

## Seslendirme metni
{plan.get('script', '')}

## CTA
{plan.get('cta', '')}

## SEO etiketleri
{tags}
"""


__all__ = ["build_local_plan", "generate_content_plan", "render_markdown"]
