"""SkillOpt dataloader for the committed WebMall split.

The test split is loaded as empty: training code never sees test tasks.
"""
from __future__ import annotations

from pathlib import Path

from skillopt.datasets.base import SplitDataLoader
from webmall_skills.skillopt_webmall.tasks import load_task_index


class WebMallDataLoader(SplitDataLoader):
    def load_split_items(self, split_path: str) -> list[dict]:
        if Path(split_path).name == "test":
            return []
        index = load_task_index()
        return [
            {**index[it["id"]], **it, "task_type": it["category"]}
            for it in super().load_split_items(split_path)
        ]
