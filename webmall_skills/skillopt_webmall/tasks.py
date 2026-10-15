"""WebMall task index for the SkillOpt integration."""
from __future__ import annotations

import json
import re
from pathlib import Path

from webmall_skills.paths import REPO_ROOT, TASK_SETS_PATH, results_root  # noqa: F401  (re-exported)

# Task types whose wrong submissions WebMall does not count against precision
# (analyze_agentlab_results/summarize_study.read_goal_achievement_data).
NO_PENALTY_TASK_TYPES = {
    "Webmall_Add_To_Cart_Task",
    "Webmall_Checkout_Task",
    "Webmall_EndToEnd_Task",
}


def _strip_task_tags(text: str) -> str:
    # task texts contain a literal backslash-n, not a newline
    return re.sub(r"</?task>|\\n", " ", text).strip()


def load_task_index(path: Path = TASK_SETS_PATH) -> dict[str, dict]:
    task_sets = json.loads(Path(path).read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for task_set in task_sets:
        for t in task_set["tasks"]:
            index[t["id"]] = {
                "id": t["id"],
                "category": t["category"],
                "task_set_id": task_set["id"],
                "task_text": _strip_task_tags(t["task"]),
            }
    return index


def task_type(task_id: str) -> str:
    """'Webmall_Checkout_Task3' -> 'Webmall_Checkout_Task' (same rule as summarize_study)."""
    m = re.match(r"^(.*?_Task)\d+$", task_id)
    return m.group(1) if m else "Unknown_Task"


def gym_task_name(task_id: str) -> str:
    return f"webmall.{task_id}"
