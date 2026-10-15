"""Run SkillOpt on WebMall.

Registers the "webmall" environment in SkillOpt's registry and calls SkillOpt's own
training entry point, so no vendored file is modified. Run from the repo root:

    Browsergym/.venv/bin/python -m webmall_skills.skillopt_webmall.train --out_root skillopt_results/c3_full

--config defaults to C3_CONFIG (configs/c3.yaml). Any SkillOpt CLI option works
(e.g. --cfg-options train.num_epochs=1 for the pilot).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from webmall_skills.paths import REPO_ROOT, resolve

C3_CONFIG = Path(__file__).resolve().parent / "configs/c3.yaml"


def configure_env() -> None:
    """Point SkillOpt's openai_compatible backend at the OpenAI API (before it is imported)."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is missing (set it in .env at the repo root)")
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", key)
    os.environ.setdefault("OPENAI_COMPATIBLE_BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_COMPATIBLE_MAX_TOKENS", "32000")


def register():
    from scripts import train as skillopt_train
    from webmall_skills.skillopt_webmall.adapter import WebMallAdapter
    from webmall_skills.skillopt_webmall.openai_compat import use_max_completion_tokens

    use_max_completion_tokens()

    skillopt_train._ENV_REGISTRY["webmall"] = WebMallAdapter
    return skillopt_train


def check_paths(cfg: dict) -> None:
    """SkillOpt starts from a blank skill if skill_init is missing; refuse instead."""
    for key in ("skill_init", "split_dir"):
        value = cfg.get(key)
        if value and not resolve(value).exists():
            raise SystemExit(f"env.{key} not found: {value} (resolved to {resolve(value)})")


def main() -> None:
    if "--config" not in sys.argv:
        sys.argv[1:1] = ["--config", str(C3_CONFIG)]
    os.chdir(REPO_ROOT)  # SkillOpt resolves skill_init/split_dir/out_root against the cwd
    configure_env()
    skillopt_train = register()
    from webmall_skills.skillopt_webmall.budget import BudgetExceeded

    check_paths(skillopt_train.load_config(skillopt_train.parse_args()))
    try:
        skillopt_train.main()
    except BudgetExceeded as e:
        print(f"\n[budget] {e}\nTraining stopped; best_skill.md in out_root is the best skill so far.")
        sys.exit(3)


if __name__ == "__main__":
    main()
