from __future__ import annotations

from pathlib import Path


def test_build_video_project_uses_workflow_data():
    from video_pipeline import build_video_project

    project = build_video_project(
        game_name="CS2",
        platform="PC",
        style="eğlenceli ve hızlı",
        tone="heyecanlı",
        duration_minutes=8,
    )

    assert "workflow" in project
    assert project["title"].startswith("CS2")
    assert project["video_path"].endswith(".mp4")
    assert len(project["script_lines"]) >= 1


def test_build_youtube_upload_body_has_required_sections():
    from video_pipeline import build_youtube_upload_body

    body = build_youtube_upload_body(
        title="CS2 PC İncelemesi",
        description="Oyun incelemesi",
        tags=["CS2", "PC", "oyun"]
    )

    assert "snippet" in body
    assert "status" in body
    assert body["snippet"]["title"] == "CS2 PC İncelemesi"
    assert body["status"]["privacyStatus"] == "private"


def test_output_dir_path_is_created_in_project():
    from video_pipeline import build_video_project

    project = build_video_project(
        game_name="Zelda",
        platform="Switch",
        style="analitik",
        tone="merak uyandırıcı",
        duration_minutes=7,
        output_dir=Path("tmp_test_output"),
    )

    assert "project_dir" in project
    assert "video_path" in project
    assert project["project_dir"].startswith("tmp_test_output") or project["project_dir"].endswith("zelda-switch")
