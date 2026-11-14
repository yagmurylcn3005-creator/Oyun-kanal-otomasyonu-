import json

from services.content_pipeline import build_local_plan


def test_build_local_plan_has_expected_fields():
    plan = build_local_plan(
        game_name="Helldivers 2",
        platform="PC",
        style="eğlenceli ve hızlı",
        tone="heyecanlı",
        duration_minutes=8,
    )

    assert plan["title"]
    assert plan["hook"]
    assert plan["outline"]
    assert plan["shot_list"]
    assert plan["cta"]
    assert plan["seo_tags"][0] == "Helldivers 2"
    assert "thumbnail_prompt" in plan


def test_build_local_plan_is_json_serializable():
    plan = build_local_plan(
        game_name="Stardew Valley",
        platform="PC",
        style="sakin ve keyifli",
        tone="samimi",
        duration_minutes=6,
    )

    serialized = json.dumps(plan, ensure_ascii=False)
    assert "Stardew Valley" in serialized
