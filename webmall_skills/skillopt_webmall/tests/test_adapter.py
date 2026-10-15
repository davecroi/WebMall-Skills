import json

import pytest

from skillopt.datasets.base import BatchSpec
from webmall_skills.paths import SKILLS_DIR
from webmall_skills.skillopt_webmall.adapter import WebMallAdapter, WebMallBatch
from webmall_skills.skillopt_webmall.trajectory import StepView
from webmall_skills.split.make_split import SPLIT_V2_DIR

BASE = (SKILLS_DIR / "base/SKILL.md").read_text()


def outcome(task_id, f1):
    return {"task_id": task_id, "gold_ids": ["answer1"], "submitted": ["answer1"] if f1 else [],
            "gold_urls": ["g"], "found_urls": ["g"] if f1 else [], "wrong_urls": [],
            "cr": int(f1 == 1.0), "precision": f1, "recall": f1, "f1": f1, "n_steps": 3,
            "input_tokens": 100_000, "output_tokens": 1_000, "err_msg": None, "env_error": False}


@pytest.fixture
def adapter(tmp_path):
    calls = []

    def run_fn(task_ids, skill_text, skill_name, study_dir, n_jobs):
        calls.append((list(task_ids), skill_text, str(study_dir)))
        return {t: tmp_path / "exp" / t for t in task_ids}

    a = WebMallAdapter(split_dir=str(SPLIT_V2_DIR), price_input_per_m=1.0, price_output_per_m=10.0,
                       val_repeats=1, cache_dir=str(tmp_path / "cache"),
                       budget_ledger=str(tmp_path / "ledger.json"), run_fn=run_fn, outcome_fn=lambda d, t: outcome(t, 0.5),
                       steps_fn=lambda d: [StepView(0, "u", "t", "", "click('1')", "", "TREE")])
    a.setup({"split_mode": "split_dir", "split_dir": str(SPLIT_V2_DIR), "out_root": str(tmp_path)})
    a.calls = calls
    return a


def val_batch(a):
    return a.build_env_from_batch(a.dataloader.build_eval_batch(env_num=0, split="valid_seen", seed=42))


def test_requires_prices(tmp_path):
    with pytest.raises(ValueError):
        WebMallAdapter(split_dir=str(SPLIT_V2_DIR), cache_dir=str(tmp_path))


def test_test_split_loads_empty(adapter):
    assert adapter.dataloader.test_items == []
    assert len(adapter.dataloader.train_items) == 26
    assert adapter.dataloader.val_items[0]["task_text"]


def test_test_split_rollout_refused(adapter, tmp_path):
    with pytest.raises(RuntimeError):
        adapter.rollout(WebMallBatch("valid_unseen", [{"id": "x"}]), BASE, str(tmp_path / "o"))


def test_val_runs_two_repeats_and_caches(adapter, tmp_path):
    adapter.val_repeats = 2                            # the adapter default (C3 uses 1)
    batch = val_batch(adapter)
    res = adapter.rollout(batch, BASE, str(tmp_path / "v1"))
    assert len(res) == 42 and res[0]["id"].endswith("@r0") and res[1]["id"].endswith("@r1")
    assert res[0]["soft"] == 0.5 and res[0]["hard"] == 0
    assert len(adapter.calls) == 2                     # one AgentLab batch per repeat
    summary = json.loads((tmp_path / "v1" / "summary.json").read_text())
    assert summary["n"] == 42 and summary["soft"] == 0.5 and summary["webmall"] is not None
    adapter.rollout(batch, BASE, str(tmp_path / "v2"))
    assert len(adapter.calls) == 2                     # served from cache


def test_train_writes_conversations_and_is_not_cached(adapter, tmp_path):
    batch = adapter.build_env_from_batch(BatchSpec("train", "train", 1, 26,
                                                   adapter.dataloader.train_items))
    res = adapter.rollout(batch, BASE, str(tmp_path / "t1"))
    assert len(res) == 26 and "@" not in res[0]["id"]
    assert res[0]["task_description"] and res[0]["task_type"]
    conv = json.loads((tmp_path / "t1" / "predictions" / res[0]["id"] / "conversation.json").read_text())
    assert conv[-1]["role"] == "system"
    adapter.rollout(batch, BASE, str(tmp_path / "t2"))
    assert len(adapter.calls) == 2                     # train is never cached


def test_leaking_candidate_rejected_without_rollouts(adapter, tmp_path):
    slug = sorted(adapter.blocklist.slugs)[0]
    res = adapter.rollout(val_batch(adapter), BASE + f"\n- See /product/{slug}/\n", str(tmp_path / "l"))
    assert len(res) == 21 and all(r["soft"] == 0 and r["hard"] == 0 for r in res)
    assert adapter.calls == []
    assert json.loads((tmp_path / "l" / "leakage_report.json").read_text())["hits"]


def test_no_skill_probe_rollout(adapter, tmp_path):
    res = adapter.rollout(val_batch(adapter), "", str(tmp_path / "n"), repeats=1)
    assert len(res) == 21 and adapter.calls[0][1] is None


def test_budget_ceiling_stops_before_running(adapter, tmp_path):
    from webmall_skills.skillopt_webmall.budget import BudgetExceeded
    adapter.budget.ceiling_usd = 0.5                    # 21 x default 0.10 > 0.5
    with pytest.raises(BudgetExceeded):
        adapter.rollout(val_batch(adapter), BASE, str(tmp_path / "b"))
    assert adapter.calls == []


def test_env_error_val_records_are_not_cached(adapter, tmp_path):
    adapter.outcome_fn = lambda d, t: {**outcome(t, 0.0), "env_error": True, "err_msg": "boom"}
    batch = val_batch(adapter)
    adapter.rollout(batch, BASE, str(tmp_path / "v1"))
    assert len(adapter.calls) == 1
    adapter.rollout(batch, BASE, str(tmp_path / "v2"))
    assert len(adapter.calls) == 2                     # env errors were re-run, not cached


def test_train_budget_check_includes_following_validation(adapter, tmp_path):
    from webmall_skills.skillopt_webmall.budget import BudgetExceeded
    adapter.budget.ceiling_usd = 3.0                   # 26 rollouts at 0.10 fit, 26 + 21 do not
    batch = adapter.build_env_from_batch(BatchSpec("train", "train", 1, 26,
                                                   adapter.dataloader.train_items))
    with pytest.raises(BudgetExceeded):
        adapter.rollout(batch, BASE, str(tmp_path / "t1"))
    assert adapter.calls == []


def test_ledger_saved_at_end_of_every_rollout(adapter, tmp_path):
    ledger = tmp_path / "ledger.json"
    bl_slug = sorted(adapter.blocklist.slugs)[0]
    adapter.rollout(val_batch(adapter), f"Use /product/{bl_slug}/", str(tmp_path / "leak"))
    assert adapter.calls == [] and ledger.exists()      # leakage-reject path saves
    ledger.unlink()
    adapter.rollout(val_batch(adapter), BASE, str(tmp_path / "v1"))
    ledger.unlink()
    adapter.rollout(val_batch(adapter), BASE, str(tmp_path / "v2"))   # all cached
    assert ledger.exists()


def test_summary_reports_agentlab_cost(adapter, tmp_path):
    adapter.outcome_fn = lambda d, t: {**outcome(t, 0.5), "agentlab_cost": 0.25}
    adapter.rollout(val_batch(adapter), BASE, str(tmp_path / "v1"))
    summary = json.loads((tmp_path / "v1" / "summary.json").read_text())
    assert summary["agentlab_cost"] == pytest.approx(0.25 * 21)
