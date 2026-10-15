"""Single source of every path used by webmall_skills.

All paths are anchored at the repository root, never at the current working directory,
so scripts, tests and IDE run configs behave the same from any folder.
"""
from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
SKILLS_DIR = PACKAGE_DIR / "skills"
TASK_SETS_PATH = REPO_ROOT / "Browsergym/browsergym/webmall/src/browsergym/webmall/task_sets.json"


def results_root() -> Path:
    """Raw experiment outputs (AgentLab runs, run dirs, caches, ledgers): the git-ignored
    folder <repo>/skillopt_results. SKILLOPT_RESULTS_DIR overrides it (empty = unset)."""
    return Path(os.environ.get("SKILLOPT_RESULTS_DIR") or REPO_ROOT / "skillopt_results")


def resolve(p: str | Path) -> Path:
    """Absolute paths stay as they are; relative paths are taken relative to REPO_ROOT."""
    p = Path(p)
    return p if p.is_absolute() else REPO_ROOT / p
