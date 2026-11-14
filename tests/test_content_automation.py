import json

from content_automation import build_local_plan, generate_content_plan


def test_build_local_plan_has_expected_fields():
    plan = build_local_plan("Helldivers 2", "PC", "eğlenceli ve hızlı", "heyecanlı", 8)
    assert plan["title"]
    assert plan["hook"]
    assert plan["outline"]
    assert plan["shot_list"]
    assert plan["script"]
    assert plan["cta"]
    assert plan["seo_tags"][0] == "Helldivers 2"


def test_build_local_plan_is_json_serializable():
    plan = build_local_plan("Stardew Valley", "PC", "sakin", "samimi", 6)
    assert "Stardew Valley" in json.dumps(plan, ensure_ascii=False)


def test_generate_content_plan_uses_offline_fallback_when_disabled(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "false")
    plan = generate_content_plan("CS2", "PC", "hızlı", "heyecanlı", 8)
    assert plan["generation"]["provider"] == "offline-template"


def test_generate_content_plan_uses_ollama_and_fills_metadata(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "true")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    def fake_call(_prompt):
        return {"title": "Test", "hook": "Giriş", "summary": "Özet", "outline": ["Bölüm"],
                "shot_list": ["Görüntü"], "script": "Tam metin", "cta": "Yorum yaz", "seo_tags": ["test"]}

    monkeypatch.setattr("content_automation._call_ollama", fake_call)
    plan = generate_content_plan("CS2", "PC", "hızlı", "heyecanlı", 8)
    assert plan["generation"] == {"provider": "ollama", "model": "test-model"}
    assert plan["platform"] == "PC"
    assert plan["script"] == "Tam metin"
