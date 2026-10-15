"""Condensed WebMall trajectories for SkillOpt's reflection stage.

Mirrors what the agent had (FLAGS_AX_M): per step URL, think, memory, action and
action error; the AX tree only where it explains a decision, subject to a per-trajectory
budget. Trees are selected by priority (errors > last 2 steps > search/listing pages > other
navigation), with each tree capped at AXTREE_CHAR_CAP and total per trajectory capped at
TREE_CHAR_BUDGET. The final record holds the submission, the gold solution and the per-task
scores.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from webmall_skills.skillopt_webmall.scoring import load_step, step_files

AXTREE_CHAR_CAP = 8_000  # ~2k tokens per included step
TREE_CHAR_BUDGET = 100_000  # ~25k tokens of trees per trajectory


@dataclass
class StepView:
    step: int
    url: str
    think: str
    memory: str
    action: str | None
    error: str
    axtree: str


def _field(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _memory(agent_info) -> str:
    msgs = _field(agent_info, "chat_messages")
    if not msgs:
        return ""
    try:
        last = msgs[-1]
    except (IndexError, TypeError, KeyError):
        return ""
    content = last.get("content", "") if isinstance(last, dict) else str(last)
    if isinstance(content, list):
        content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    m = re.search(r"<memory>(.*?)</memory>", str(content), re.S)
    return m.group(1).strip() if m else ""


def load_steps(exp_dir: Path) -> list[StepView]:
    raw = [load_step(p) for p in step_files(exp_dir)]
    views: list[StepView] = []
    for i, s in enumerate(raw):
        obs = _field(s, "obs") or {}
        next_obs = (_field(raw[i + 1], "obs") or {}) if i + 1 < len(raw) else {}
        agent_info = _field(s, "agent_info")
        views.append(StepView(
            step=int(_field(s, "step", i)),
            url=str(obs.get("url", "") or ""),
            think=str(_field(agent_info, "think", "") or ""),
            memory=_memory(agent_info),
            action=_field(s, "action"),
            error=str(next_obs.get("last_action_error") or ""),
            axtree=str(obs.get("axtree_txt", "") or ""),
        ))
    return views


def _cost(axtree_text: str) -> int:
    """Calculate cost of including an AX tree (capped per step)."""
    return min(len(axtree_text), AXTREE_CHAR_CAP)


def tree_steps(steps: list[StepView]) -> set[int]:
    """Select steps to include AX trees for, subject to budget and priority tiers.

    Priority tiers (within each tier, chronological order):
    1. Acting steps with an action error
    2. Last 2 acting steps
    3. Acting steps with URL change to search/listing pages ("?s=" or "/page/")
    4. Other acting steps with URL change

    Steps with empty axtree are skipped. Selection continues until budget exhausted.
    """
    acting = [i for i, s in enumerate(steps) if s.action]
    keep = set()
    budget = TREE_CHAR_BUDGET

    # Build ordered candidate list (tiers 1-4, deduplicated, preserving order)
    candidates = []
    seen = set()

    # Tier 1: Acting steps with an action error
    for i in acting:
        if steps[i].error and i not in seen:
            candidates.append(i)
            seen.add(i)

    # Tier 2: Last 2 acting steps
    for i in acting[-2:]:
        if i not in seen:
            candidates.append(i)
            seen.add(i)

    # Tier 3: Acting steps with URL change to search/listing pages
    for i in acting:
        if i > 0 and steps[i].url != steps[i - 1].url:
            if ("?s=" in steps[i].url or "/page/" in steps[i].url) and i not in seen:
                candidates.append(i)
                seen.add(i)

    # Tier 4: Other acting steps with URL change
    for i in acting:
        if i > 0 and steps[i].url != steps[i - 1].url and i not in seen:
            candidates.append(i)
            seen.add(i)

    # Select candidates in order, respecting budget
    for i in candidates:
        if steps[i].axtree:  # Skip empty axtree
            cost = _cost(steps[i].axtree)
            if cost <= budget:
                keep.add(i)
                budget -= cost

    return keep


def _cap(text: str) -> str:
    if len(text) <= AXTREE_CHAR_CAP:
        return text
    return text[:AXTREE_CHAR_CAP] + "\n... [AX tree truncated]"


def _evaluation(outcome: dict) -> str:
    found = set(outcome.get("found_urls", []))
    missing = [u for u in outcome.get("gold_urls", []) if u not in found]
    lines = [
        "Evaluation of the final submission:",
        f"CR={outcome.get('cr', 0)} P={outcome.get('precision', 0):.2f} "
        f"R={outcome.get('recall', 0):.2f} F1={outcome.get('f1', 0):.2f}",
        "Correct offers submitted: " + (", ".join(sorted(found)) or "none"),
        "Gold offers missing: " + (", ".join(missing) or "none"),
        "Wrong offers submitted: " + (", ".join(outcome.get("wrong_urls", [])) or "none"),
    ]
    if outcome.get("env_error"):
        lines.append(f"Run ended with an error: {outcome.get('err_msg')}")
    return "\n".join(lines)


def build_conversation(steps: list[StepView], task_text: str, outcome: dict) -> list[dict]:
    conv: list[dict] = [{"role": "user", "content": f"Task: {task_text}"}]
    keep = tree_steps(steps)
    for i, s in enumerate(steps):
        if not s.action:
            continue
        if i in keep and s.axtree:
            conv.append({"role": "observation",
                         "content": f"URL: {s.url}\nAX tree seen before this action:\n{_cap(s.axtree)}"})
        reasoning = s.think + (f"\n[memory] {s.memory}" if s.memory else "")
        feedback = f"url={s.url}" + (f"; action error: {s.error}" if s.error else "")
        conv.append({"step": s.step, "reasoning": reasoning, "action": s.action,
                     "env_feedback": feedback})
    conv.append({"role": "system", "content": _evaluation(outcome)})
    return conv
