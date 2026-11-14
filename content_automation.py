from services.content_pipeline import build_output, generate_workflow_output


def test_generate_workflow_output_returns_expected_sections():
    workflow = generate_workflow_output(
        game_name="Elden Ring",
        platform="PC",
        style="analitik",
        tone="derin",
        duration_minutes=10,
        api_key=None,
    )

    assert "plan" in workflow
    assert "script_lines" in workflow
    assert "script_text" in workflow
    assert "youtube_meta" in workflow
    assert "thumbnail_prompt" in workflow
    assert workflow["youtube_meta"]["title"]


def test_build_output_supports_thumbnail_mode():
    output = build_output(
        mode="thumbnail",
        game="Fortnite",
        platform="PS5",
        style="hızlı ve enerjik",
        tone="heyecanlı",
        duration=7,
        api_key=None,
    )

    assert "Fortnite" in output
    assert "thumbnail" in output.lower()
