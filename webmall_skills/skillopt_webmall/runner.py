"""Run WebMall tasks through AgentLab with a given skill text.

Uses the same agent (AGENT_GPT6_LUNA_AX_M), skill injection (webmall_skills.injection.with_skill),
benchmark settings (webmall_v1.0: max 50 steps, headless) as the test runs.
"""
from __future__ import annotations

import copy
import json
import logging
from pathlib import Path

from agentlab.experiments.launch_exp import run_experiments
from webmall_skills.injection import with_skill
from webmall_skills.skillopt_webmall.agent_config import AGENT_GPT6_LUNA_AX_M
from webmall_skills.skillopt_webmall.tasks import gym_task_name
from webmall_overrides.configs import WEBMALL_BENCHMARKS
from webmall_overrides.env_args import EnvArgsWebMall
from webmall_overrides.exp_args import ExpArgsWebMall

MAX_STEPS = 50


def build_agent(skill_text: str | None, skill_name: str):
    if skill_text:
        agent = copy.deepcopy(
            with_skill(AGENT_GPT6_LUNA_AX_M, skill_text=skill_text, skill_name=skill_name))
    else:
        agent = copy.deepcopy(AGENT_GPT6_LUNA_AX_M)
    agent.set_benchmark(WEBMALL_BENCHMARKS["webmall_v1.0"](), False)
    return agent


def make_exp_args(task_ids: list[str], agent_args) -> list[ExpArgsWebMall]:
    return [
        ExpArgsWebMall(
            agent_args=agent_args,
            env_args=EnvArgsWebMall(
                # WebMall tasks are deterministic (seed only goes to the base task); fixed seed matches test runs
                task_name=gym_task_name(t), task_seed=0, max_steps=MAX_STEPS,
                headless=True, record_video=False,
            ),
            logging_level=logging.INFO,
        )
        for t in task_ids
    ]


def has_env_error(exp_dir: Path) -> bool:
    p = Path(exp_dir) / "summary_info.json"
    if not p.exists():
        return True
    return bool(json.loads(p.read_text()).get("err_msg"))


def _run(task_ids, agent, study_dir, n_jobs) -> dict[str, Path]:
    exps = make_exp_args(task_ids, agent)
    run_experiments(
        n_jobs=n_jobs, exp_args_list=exps, study_dir=study_dir,
        parallel_backend="sequential" if n_jobs == 1 else "ray",
    )
    return {t: Path(e.exp_dir) for t, e in zip(task_ids, exps)}


def run_tasks(task_ids: list[str], skill_text: str | None, skill_name: str,
              study_dir: Path, n_jobs: int = 1) -> dict[str, Path]:
    """Run tasks once and relaunch env-error tasks once into study_dir/relaunch.

    Task ids must be unique (results are keyed by id); repeats must be separate calls.
    Tasks still failing after the relaunch are returned as-is; detect them with has_env_error.
    """
    dup = sorted({t for t in task_ids if task_ids.count(t) > 1})
    if dup:
        raise ValueError(f"duplicate task ids: {dup}")
    agent = build_agent(skill_text, skill_name)
    dirs = _run(task_ids, agent, Path(study_dir), n_jobs)
    failed = [t for t, d in dirs.items() if has_env_error(d)]
    if failed:
        logging.warning("relaunching %d task(s) after env errors: %s", len(failed), failed)
        first = {t: dirs[t] for t in failed}
        dirs.update(_run(failed, agent, Path(study_dir) / "relaunch", n_jobs))
        for t in failed:
            # scoring.read_outcome adds the failed attempt's tokens so the ledger counts them
            Path(dirs[t]).mkdir(parents=True, exist_ok=True)
            (Path(dirs[t]) / "first_attempt.txt").write_text(str(first[t]))
    return dirs
