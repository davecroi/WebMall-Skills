"""The evaluated DeepSeek agent, imported from run_webmall_study.py.

run_webmall_study.py sets the root logger to DEBUG at import time; restore the level.
Run every entry point as `python -m webmall_skills…` from the repo root.
"""
import logging

_level = logging.getLogger().level
from run_webmall_study import AGENT_DEEPSEEK_V41_FLASH_AX_M  # noqa: E402,F401

logging.getLogger().setLevel(_level)
