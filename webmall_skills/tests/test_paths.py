import os
from pathlib import Path

from webmall_skills import paths


def test_repo_root_is_the_webmall_checkout():
    assert (paths.REPO_ROOT / "run_webmall_study.py").exists()
    assert paths.PACKAGE_DIR == paths.REPO_ROOT / "webmall_skills"
    assert paths.TASK_SETS_PATH.exists()


def test_resolve_is_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert paths.resolve("webmall_skills/skills/base/SKILL.md").exists()
    assert paths.resolve(tmp_path) == tmp_path


def test_results_root_default_and_override(tmp_path, monkeypatch):
    monkeypatch.delenv("SKILLOPT_RESULTS_DIR", raising=False)
    assert paths.results_root() == paths.REPO_ROOT / "skillopt_results"
    monkeypatch.setenv("SKILLOPT_RESULTS_DIR", str(tmp_path))
    assert paths.results_root() == tmp_path
    monkeypatch.setenv("SKILLOPT_RESULTS_DIR", "")
    assert paths.results_root() == paths.REPO_ROOT / "skillopt_results"
