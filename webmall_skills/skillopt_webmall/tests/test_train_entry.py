import sys

import pytest

from webmall_skills.skillopt_webmall import train as train_skillopt
from webmall_skills.skillopt_webmall.adapter import WebMallAdapter
from webmall_skills.skillopt_webmall.train import check_paths


@pytest.fixture(autouse=True)
def fake_env(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("SKILLOPT_RESULTS_DIR", str(tmp_path))


def load(monkeypatch, tmp_path, *overrides):
    mod = train_skillopt.register()
    monkeypatch.setattr(sys, "argv", [
        "train", "--config", str(train_skillopt.C3_CONFIG), "--out_root", str(tmp_path / "run"),
        "--cfg-options", "env.price_input_per_m=1.0", "env.price_output_per_m=10.0", *overrides,
    ])
    return mod, mod.load_config(mod.parse_args())


def test_config_values(monkeypatch, tmp_path):
    _, cfg = load(monkeypatch, tmp_path)
    assert cfg["env"] == "webmall"
    assert cfg["optimizer_model"] == cfg["target_model"] == "deepseek/deepseek-v4.1-flash"
    assert cfg["optimizer_backend"] == "openai_compatible"
    assert cfg["gate_metric"] == "soft"
    assert cfg["use_slow_update"] is False and cfg["use_meta_skill"] is False
    assert cfg["eval_test"] is False
    assert cfg["num_epochs"] == 4 and cfg["batch_size"] == 13
    assert cfg["edit_budget"] == 4 and cfg["minibatch_size"] == 4
    assert cfg["val_repeats"] == 1 and cfg["budget_usd"] == 25
    assert cfg["split_dir"] == "webmall_skills/split/split_v2"


def test_adapter_built_from_config(monkeypatch, tmp_path):
    mod, cfg = load(monkeypatch, tmp_path)
    a = mod.get_adapter(cfg)
    assert isinstance(a, WebMallAdapter)
    assert a.val_repeats == 1 and a.edit_budget == 4 and a.minibatch_size == 4
    a.setup(cfg)
    assert len(a.dataloader.train_items) == 26 and len(a.dataloader.val_items) == 21


def test_configure_env_points_at_openrouter(monkeypatch):
    for k in ("OPENAI_COMPATIBLE_API_KEY", "OPENAI_COMPATIBLE_BASE_URL", "OPENAI_COMPATIBLE_MAX_TOKENS"):
        monkeypatch.delenv(k, raising=False)
    train_skillopt.configure_env()
    import os
    assert os.environ["OPENAI_COMPATIBLE_API_KEY"] == os.environ["OPENROUTER_API_KEY"]
    assert os.environ["OPENAI_COMPATIBLE_BASE_URL"] == "https://openrouter.ai/api/v1"
    assert os.environ["OPENAI_COMPATIBLE_MAX_TOKENS"] == "32000"


def test_configure_env_does_not_require_agentlab_exp_root(monkeypatch):
    monkeypatch.delenv("AGENTLAB_EXP_ROOT", raising=False)
    monkeypatch.setattr(train_skillopt, "load_dotenv", lambda *a, **k: None)
    train_skillopt.configure_env()


def test_results_root_defaults_to_repo_folder(monkeypatch):
    from webmall_skills.paths import REPO_ROOT
    from webmall_skills.skillopt_webmall.tasks import results_root
    monkeypatch.delenv("SKILLOPT_RESULTS_DIR", raising=False)
    assert results_root() == REPO_ROOT / "skillopt_results"


def test_results_root_can_be_overridden(monkeypatch, tmp_path):
    from webmall_skills.skillopt_webmall import adapter
    from webmall_skills.skillopt_webmall.tasks import results_root
    monkeypatch.setenv("SKILLOPT_RESULTS_DIR", str(tmp_path / "elsewhere"))
    assert results_root() == tmp_path / "elsewhere" == adapter.results_root()


def test_adapter_defaults_land_in_results_root(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # split_dir is resolved against the repo root, not the cwd
    monkeypatch.setenv("SKILLOPT_RESULTS_DIR", str(tmp_path / "elsewhere"))
    a = WebMallAdapter(split_dir="webmall_skills/split/split_v2", price_input_per_m=1.0,
                       price_output_per_m=10.0, run_fn=lambda *a: {})
    assert a.cache.root == tmp_path / "elsewhere" / "rollout_cache"
    assert a.budget.ledger_path == tmp_path / "elsewhere" / "c3_ledger.json"
    a.setup({"split_mode": "split_dir", "split_dir": "webmall_skills/split/split_v2",
             "out_root": str(tmp_path / "run")})
    assert len(a.dataloader.train_items) == 26 and len(a.dataloader.val_items) == 21


def test_results_folder_is_git_ignored():
    import subprocess
    from webmall_skills.paths import REPO_ROOT
    r = subprocess.run(["git", "check-ignore", "-q", "skillopt_results/x"], cwd=REPO_ROOT)
    assert r.returncode == 0


def test_check_paths_refuses_missing_skill_init():
    with pytest.raises(SystemExit, match="skill_init"):
        check_paths({"skill_init": "webmall_skills/skills/nope/SKILL.md",
                     "split_dir": "webmall_skills/split/split_v2"})


def test_check_paths_accepts_the_c3_config_from_any_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    check_paths({"skill_init": "webmall_skills/skills/base/SKILL.md",
                 "split_dir": "webmall_skills/split/split_v2"})
