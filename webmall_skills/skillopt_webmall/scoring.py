"""Per-task WebMall scoring for SkillOpt.

Mirrors analyze_agentlab_results/summarize_study.py: gold = checklist goals with id
answerN; submitted = achieved answer goals plus wrong solutions (wrong solutions are
not counted for cart/checkout/end-to-end tasks). CR = exact set match.
"""
from __future__ import annotations

import gzip
import json
import pickle
import re
from pathlib import Path

from analyze_agentlab_results.summarize_study import calculation_results
from webmall_skills.skillopt_webmall.tasks import NO_PENALTY_TASK_TYPES, task_type

_ANSWER_ID = re.compile(r"^answer\d+$")


def solution_sets(task_info: dict | None, task_id: str) -> dict:
    empty = {"gold_ids": set(), "submitted": set(), "gold_urls": [], "found_urls": [], "wrong_urls": []}
    if not task_info or "checklist" not in task_info:
        return empty
    answers = [
        cp for cp in task_info["checklist"]
        if isinstance(cp, dict) and _ANSWER_ID.match(str(cp.get("id", "")))
    ]
    found = [cp for cp in answers if cp.get("flag")]
    wrong = [] if task_type(task_id) in NO_PENALTY_TASK_TYPES else [
        str(w) for w in (task_info.get("wrong_solutions") or [])
    ]
    return {
        "gold_ids": {cp["id"] for cp in answers},
        "submitted": {cp["id"] for cp in found} | set(wrong),
        "gold_urls": [str(cp.get("value", "")) for cp in answers],
        "found_urls": [str(cp.get("value", "")) for cp in found],
        "wrong_urls": wrong,
    }


def task_metrics(gold: set, submitted: set) -> dict:
    hit = len(gold & submitted)
    precision = hit / len(submitted) if submitted else 0.0
    recall = hit / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    return {"cr": int(gold == submitted), "precision": precision, "recall": recall, "f1": f1}


def aggregate(records: list[dict]) -> dict:
    """WebMall's aggregate (F1 from averaged P and R) over outcome records."""
    return calculation_results(
        [set(r["gold_ids"]) for r in records],
        [set(r["submitted"]) for r in records],
    )


def step_files(exp_dir: Path) -> list[Path]:
    return sorted(
        Path(exp_dir).glob("step_*.pkl.gz"),
        key=lambda p: int(re.search(r"step_(\d+)", p.name).group(1)),
    )


def load_step(path: Path):
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


def read_outcome(exp_dir: Path, task_id: str) -> dict:
    exp_dir = Path(exp_dir)
    summary_path = exp_dir / "summary_info.json"
    info = json.loads(summary_path.read_text()) if summary_path.exists() else None
    files = step_files(exp_dir)
    task_info = getattr(load_step(files[-1]), "task_info", None) if files else None
    sets = solution_sets(task_info, task_id)
    info = info or {}
    env_error = (not summary_path.exists()) or bool(info.get("err_msg"))
    metrics = task_metrics(sets["gold_ids"], sets["submitted"])
    # Crashed or no-checklist runs score 0 (not "set match on empty" = 1).
    if env_error or not sets["gold_ids"]:
        metrics["cr"] = 0
    in_tok = int(info.get("stats.cum_input_tokens", 0))
    out_tok = int(info.get("stats.cum_output_tokens", 0))
    cost = float(info.get("stats.cum_cost", 0.0))
    marker = exp_dir / "first_attempt.txt"
    if marker.exists():  # relaunched task: the failed first attempt was paid for too
        fp = Path(marker.read_text().strip()) / "summary_info.json"
        first = json.loads(fp.read_text()) if fp.exists() else {}
        in_tok += int(first.get("stats.cum_input_tokens", 0))
        out_tok += int(first.get("stats.cum_output_tokens", 0))
        cost += float(first.get("stats.cum_cost", 0.0))
    return {
        "task_id": task_id,
        "gold_ids": sorted(sets["gold_ids"]),
        "submitted": sorted(sets["submitted"]),
        "gold_urls": sets["gold_urls"],
        "found_urls": sets["found_urls"],
        "wrong_urls": sets["wrong_urls"],
        **metrics,
        "n_steps": int(info.get("n_steps", max(len(files) - 1, 0))),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "agentlab_cost": cost,
        "err_msg": info.get("err_msg"),
        "env_error": env_error,
    }
