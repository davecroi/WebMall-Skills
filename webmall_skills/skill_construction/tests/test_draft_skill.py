from webmall_skills.skill_construction.draft_skill import MODEL, build_request


def test_request_has_fixed_model_and_no_temperature():
    req = build_request("PROMPT", "SRC", "FND")
    assert req["model"] == MODEL == "gpt-6.1-sol"
    assert "temperature" not in req
    assert req["reasoning_effort"] == "high"


def test_request_contains_prompt_and_both_inputs_only():
    req = build_request("PROMPT", "SRC", "FND")
    content = "\n".join(m["content"] for m in req["messages"])
    assert "PROMPT" in content and "SRC" in content and "FND" in content
    assert [m["role"] for m in req["messages"]] == ["user"]
