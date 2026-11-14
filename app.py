from __future__ import annotations

import json
import re
from typing import Any, Dict


def _extract_json_text(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Boş model yanıtı.")

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    return json.loads(text)


def generate_structured_response(prompt: str, api_key: str) -> Dict[str, Any]:
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw_text = getattr(response, "text", None) or str(response)
        return _extract_json_text(raw_text)
    except Exception as exc:  # pragma: no cover - exercised in runtime fallback
        raise RuntimeError(f"Gemini çağrısı başarısız: {exc}") from exc
