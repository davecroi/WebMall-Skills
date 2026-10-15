"""
GenericAgent variant that injects a SKILL.md file into the prompt.

The skill text is appended to the flags' `extra_instructions`, so it appears
in the "## Extra instructions" section of the user message at every step,
wrapped in the same "## Skill Knowledge" text SkillOpt's ALFWorld env uses.
With `skill_path=None` the agent behaves exactly like `GenericAgent`, which
gives the no-skill baseline.
"""

from dataclasses import dataclass
from pathlib import Path

from agentlab.agents.generic_agent.generic_agent import GenericAgent, GenericAgentArgs

from webmall_skills.paths import SKILLS_DIR, resolve


@dataclass
class SkillGenericAgentArgs(GenericAgentArgs):
    skill_path: str | None = None
    # Read from skill_path at construction so the exact text is saved with
    # each experiment (exp_args.pkl), even if the file changes later.
    skill_text: str | None = None
    # Used in agent_name / result folder names; defaults to the skill's folder
    # name for "SKILL.md" files, otherwise the file stem.
    skill_name: str | None = None

    def __post_init__(self):
        super().__post_init__()
        if self.skill_path is not None:
            path = Path(self.skill_path)
            if self.skill_text is None:
                self.skill_text = path.read_text(encoding="utf-8")
            if self.skill_name is None:
                self.skill_name = path.parent.name if path.name.lower() == "skill.md" else path.stem
        if self.skill_text is None:
            return
        if self.skill_name is None:
            self.skill_name = "inline"
        if getattr(self, "agent_name", None):
            self.agent_name = f"{self.agent_name}-skill_{self.skill_name}"

    def make_agent(self):
        flags = self.flags.copy()
        if self.skill_text:
            # Same wrapper as SkillOpt's ALFWorld rollout (skillopt/envs/alfworld/rollout.py),
            # so skills are evaluated in the format they are trained in.
            skill_block = (
                "## Skill Knowledge\n"
                "Below is a skill document with learned strategies. "
                "Use these guidelines to inform your decisions:\n\n"
                f"{self.skill_text.strip()}"
            )
            flags.extra_instructions = "\n\n".join(
                part for part in (flags.extra_instructions, skill_block) if part
            )
        return GenericAgent(
            chat_model_args=self.chat_model_args, flags=flags, max_retry=self.max_retry
        )


def with_skill(
    agent_args: GenericAgentArgs,
    skill_path: str | None = None,
    *,
    skill_text: str | None = None,
    skill_name: str | None = None,
) -> GenericAgentArgs:
    """Return a copy of `agent_args` that uses the given skill (None = baseline).

    Pass either a SKILL.md path or the skill text itself (used by SkillOpt rollouts,
    where the candidate skill only exists in memory).
    """
    if skill_path is None and skill_text is None:
        return agent_args
    if not isinstance(agent_args, GenericAgentArgs):
        raise TypeError(
            f"with_skill needs agentlab.agents.generic_agent.GenericAgentArgs, got "
            f"{type(agent_args).__module__}.{type(agent_args).__name__}; the WebMall presets "
            "(agentlab.agents.webmall_generic_agent) use a different agent class")
    return SkillGenericAgentArgs(
        chat_model_args=agent_args.chat_model_args,
        flags=agent_args.flags,
        max_retry=agent_args.max_retry,
        skill_path=None if skill_path is None else str(skill_path),
        skill_text=skill_text,
        skill_name=skill_name,
    )


def available_skills() -> list[str]:
    return sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))


def skill_path(name: str | Path | None) -> Path | None:
    """None -> no skill; "base" -> webmall_skills/skills/base/SKILL.md; a path -> that file."""
    if name is None:
        return None
    p = Path(name)
    if p.suffix.lower() != ".md":
        p = SKILLS_DIR / str(name) / "SKILL.md"
    elif not p.is_absolute():
        p = resolve(p)
    if not p.exists():
        raise FileNotFoundError(f"skill {name!r} not found ({p}); available: {available_skills()}")
    return p
