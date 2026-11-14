import json

from autopilot import choose_next_topic, load_topics, mark_topic_generated


def test_topic_rotation_selects_least_recently_generated(tmp_path):
    state = tmp_path / "state.json"
    topics = [{"game": "A"}, {"game": "B"}]
    mark_topic_generated("A", state)
    assert choose_next_topic(topics, state)["game"] == "B"
    mark_topic_generated("B", state)
    assert choose_next_topic(topics, state)["game"] == "A"


def test_invalid_topic_config_falls_back_to_defaults(tmp_path):
    path = tmp_path / "topics.json"
    path.write_text("not json", encoding="utf-8")
    assert load_topics(path)


def test_load_topics_reads_custom_list(tmp_path):
    path = tmp_path / "topics.json"
    path.write_text(json.dumps({"topics": [{"game": "Custom", "duration": 5}]}), encoding="utf-8")
    assert load_topics(path) == [{"game": "Custom", "platform": "PC", "style": "eğlenceli ve hızlı", "tone": "heyecanlı", "duration": 5}]
