import json

from video_workflow_core import generate_workflow_output
from video_workflow import save_package


def test_generate_workflow_output_contains_all_assets(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "false")
    workflow = generate_workflow_output("Zelda", "Switch", "sakin", "samimi", 7)
    assert workflow["plan"]["title"]
    assert workflow["script_text"]
    assert workflow["youtube_meta"]["title"]
    assert "Açıklama" in workflow["youtube_meta_text"]


def test_save_package_writes_all_files(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "false")
    workflow = generate_workflow_output("Zelda", "Switch", "sakin", "samimi", 7)
    target = save_package(workflow, str(tmp_path), "Zelda")
    expected = {"plan.json", "summary.md", "script.txt", "youtube_meta.txt", "youtube_meta.json"}
    assert expected == {path.name for path in target.iterdir()}
    assert json.loads((target / "plan.json").read_text(encoding="utf-8"))["platform"] == "Switch"
