"""The evaluated agent (GLM-5.3-flash), imported from run_webmall_study.py.

Keep TARGET_AGENT's model in sync with model.target in configs/c3.yaml.
run_webmall_study.py sets the root logger to DEBUG at import time; restore the level.
Run every entry point as `python -m webmall_skills…` from the repo root.
"""
import logging

_level = logging.getLogger().level
from run_webmall_study import AGENT_GLM_53_FLASH_AX_M as TARGET_AGENT  # noqa: E402,F401

logging.getLogger().setLevel(_level)
