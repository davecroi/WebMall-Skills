"""Val rollout cache keyed by (skill text hash, task id, repeat).

Lets the base-skill val baseline from step 0 be reused by C3 and C4. Only val
rollouts are cached; train rollouts are always fresh.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class RolloutCache:
    def __init__(self, root: Path):
        self.root = Path(root)

    @staticmethod
    def skill_key(skill_text: str | None) -> str:
        if not skill_text:
            return "noskill"
        return hashlib.sha256(skill_text.encode("utf-8")).hexdigest()

    def _path(self, skill_text, task_id: str, repeat: int) -> Path:
        return self.root / self.skill_key(skill_text) / task_id / f"r{repeat}.json"

    def get(self, skill_text, task_id: str, repeat: int) -> dict | None:
        p = self._path(skill_text, task_id, repeat)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def put(self, skill_text, task_id: str, repeat: int, record: dict) -> None:
        p = self._path(skill_text, task_id, repeat)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, p)
