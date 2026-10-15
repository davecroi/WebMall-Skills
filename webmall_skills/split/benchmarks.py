"""WebMall benchmarks built from the committed train/val/test task split.

Same settings as webmall_overrides/configs.py (50 steps, 1 repeat, seeds from
RandomState(42)); the task list is read from split_v2 so the benchmark cannot drift
from the split the leakage guard protects. Used by run_webmall_study.py:

    benchmark = "webmall_skills_test"   # or webmall_skills_val / webmall_skills_train
"""
from __future__ import annotations

from pathlib import Path

from webmall_skills.split.make_split import SPLIT_V2_DIR, load_items


def split_task_names(split: str, split_dir: Path = SPLIT_V2_DIR) -> list[str]:
    return [f"webmall.{it['id']}" for it in load_items(split, split_dir)]


def split_benchmark(name: str, split: str, split_dir: Path = SPLIT_V2_DIR):
    import numpy as np
    from browsergym.experiments.benchmark.configs import DEFAULT_HIGHLEVEL_ACTION_SET_ARGS
    from browsergym.experiments.benchmark.metadata.utils import task_metadata
    from webmall_overrides.benchmark import WebMallBenchmark
    from webmall_overrides.utils import make_env_args_list_from_repeat_tasks

    return WebMallBenchmark(
        name=name,
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=True,
        backends=["webmall"],
        env_args_list=make_env_args_list_from_repeat_tasks(
            task_list=split_task_names(split, split_dir),
            max_steps=50,
            n_repeats=1,
            seeds_rng=np.random.RandomState(42),
        ),
        task_metadata=task_metadata("webmall"),
    )


SPLIT_BENCHMARKS = {
    f"webmall_skills_{split}": (lambda split=split: split_benchmark(f"webmall_skills_{split}", split))
    for split in ("train", "val", "test")
}


def register() -> None:
    """Make the split benchmarks selectable by name in run_webmall_study.py."""
    from webmall_overrides.configs import WEBMALL_BENCHMARKS
    WEBMALL_BENCHMARKS.update(SPLIT_BENCHMARKS)
