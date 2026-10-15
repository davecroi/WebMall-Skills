import pytest
from agentlab.agents.generic_agent.agent_configs import FLAGS_GPT_4o
from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs
from agentlab.llm.chat_api import OpenAIModelArgs

from webmall_skills.injection import (
    SkillGenericAgentArgs,
    available_skills,
    skill_path,
    with_skill,
)
from webmall_skills.paths import SKILLS_DIR

AGENT = GenericAgentArgs(
    chat_model_args=OpenAIModelArgs(model_name="gpt-6-luna", max_total_tokens=1000,
                                    max_input_tokens=900, max_new_tokens=100),
    flags=FLAGS_GPT_4o,
)


@pytest.fixture(autouse=True)
def fake_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_none_returns_original():
    assert with_skill(AGENT, None) is AGENT


def test_path_behaviour_unchanged():
    path = SKILLS_DIR / "base/SKILL.md"
    a = with_skill(AGENT, path)
    assert a.skill_text == path.read_text(encoding="utf-8")
    assert a.agent_name.endswith("-skill_base")


def test_text_injection():
    a = with_skill(AGENT, skill_text="Always scroll.", skill_name="so1234")
    assert isinstance(a, SkillGenericAgentArgs)
    assert a.skill_path is None and a.skill_text == "Always scroll."
    assert a.agent_name.endswith("-skill_so1234")
    extra = a.make_agent().flags.extra_instructions
    assert "## Skill Knowledge" in extra and "Always scroll." in extra
    # FLAGS_GPT_4o has extra_instructions=None; the shared flags must stay unmodified
    assert "Skill Knowledge" not in (AGENT.flags.extra_instructions or "")


def test_text_without_name():
    assert with_skill(AGENT, skill_text="x").skill_name == "inline"


def test_skill_path_by_name_and_none():
    assert skill_path(None) is None
    assert skill_path("base") == SKILLS_DIR / "base" / "SKILL.md"
    assert "base" in available_skills()


def test_skill_path_unknown_name_lists_available():
    with pytest.raises(FileNotFoundError, match="base"):
        skill_path("does_not_exist")


def test_with_skill_rejects_webmall_generic_agent_args():
    from agentlab.agents.webmall_generic_agent.agent_configs import AGENT_4o
    with pytest.raises(TypeError, match="generic_agent.GenericAgentArgs"):
        with_skill(AGENT_4o, skill_text="x")
