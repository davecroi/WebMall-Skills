import json

import pytest

from webmall_skills.skillopt_webmall import test_eval
from webmall_skills.skillopt_webmall.budget import Budget
from webmall_skills.skillopt_webmall.cache import RolloutCache


def rec(f1=1.0, tin=100_000, tout=2_000, steps=20, env_error=False, exp_dir="x"):
    return {"f1": f1, "cr": int(f1 == 1.0), "input_tokens": tin, "output_tokens": tout,
            "n_steps": steps, "env_error": env_error, "exp_dir": exp_dir}


def budget(tmp_path, ceiling):
    return Budget(tmp_path / "ledger.json", ceiling, 0.10, 0.50, optimizer_tokens_fn=lambda: (0, 0))


def test_check_fits():
    assert test_eval.check_fits(33, 0.03, 1.25, 0.0, 1.30) == (True, pytest.approx(1.2375))
    assert test_eval.check_fits(33, 0.03, 1.25, 1.0, 2.0)[0] is False


def test_ceiling_from_credit_then_from_ledger(tmp_path):
    ledger = tmp_path / "ledger.json"
    assert test_eval.ceiling_for(ledger, 0.5, 3.0) == 3.5
    with pytest.raises(SystemExit):
        test_eval.ceiling_for(ledger, 0.5, None)
    ledger.write_text(json.dumps({"ceiling_usd": 3.78}))
    assert test_eval.ceiling_for(ledger, 1.2, None) == 3.78


def test_per_run_estimate_uses_cached_val_runs(tmp_path):
    cache = RolloutCache(tmp_path)
    cache.put("skill", "A", 0, rec(tin=200_000, tout=4_000))  # $0.022
    assert test_eval.per_run_estimate(cache, "skill", ["A", "B"], 0.10, 0.50) == pytest.approx(0.022)
    assert test_eval.per_run_estimate(cache, None, ["A"], 0.10, 0.50) == test_eval.DEFAULT_RUN_USD


def fake_run(tmp_path, f1s):
    calls = []

    def run_fn(task_ids, text, name, study_dir, n_jobs):
        calls.append(task_ids)
        return {t: tmp_path / t for t in task_ids}

    def outcome_fn(exp_dir, tid):
        return rec(f1=f1s.get(tid, 1.0), env_error=tid == "ERR")

    return calls, run_fn, outcome_fn


def test_run_condition_runs_one_at_a_time_and_skips_cached(tmp_path):
    cache = RolloutCache(tmp_path / "cache")
    cache.put(None, "A", 0, rec())
    calls, run_fn, outcome_fn = fake_run(tmp_path, {"B": 0.5})
    b = budget(tmp_path, 10.0)
    items = [{"id": t} for t in ("A", "B", "ERR")]
    assert test_eval.run_condition("noskill", b, cache, items, tmp_path / "out", 0.02, 1.25,
                                   run_fn, outcome_fn) is True
    assert calls == [["B"], ["ERR"]]
    assert cache.get(None, "B", 0)["f1"] == 0.5
    assert cache.get(None, "ERR", 0) is None  # env errors are retried on the next call
    assert b.rollouts == 2


def test_run_condition_safety_stop(tmp_path):
    cache = RolloutCache(tmp_path / "cache")
    calls, run_fn, outcome_fn = fake_run(tmp_path, {})
    b = budget(tmp_path, 0.03)  # each fake run costs $0.011
    items = [{"id": t} for t in ("A", "B", "C")]
    assert test_eval.run_condition("noskill", b, cache, items, tmp_path / "out", 0.01, 1.0,
                                   run_fn, outcome_fn) is False
    assert calls == [["A"], ["B"]]


def test_build_summary_with_partial_conditions(tmp_path, monkeypatch):
    monkeypatch.setattr(test_eval, "skill_text", lambda c: None if c == "noskill" else c)
    cache = RolloutCache(tmp_path)
    items = [{"id": "A", "category": "X"}, {"id": "B", "category": "Y"}]
    md, result = test_eval.build_summary(cache, items, 0.10, 0.50)
    assert "No condition has been run yet" in md and result["conditions"] == {}
    for t, f1 in (("A", 1.0), ("B", 0.0)):
        cache.put("best", t, 0, rec(f1=f1, exp_dir=str(tmp_path / "none")))
    cache.put(None, "A", 0, rec(f1=0.5, exp_dir=str(tmp_path / "none")))
    md, result = test_eval.build_summary(cache, items, 0.10, 0.50)
    assert set(result["conditions"]) == {"best", "noskill"}
    assert result["conditions"]["best"]["score"]["f1"] == 0.5
    assert result["conditions"]["noskill"]["score"]["missing"] == 1
    assert "Δ best (C3 v0007) vs. no skill" in md
    assert "Mean per test run" in md
    assert "| A | X | 1.000 | 0.500 | +0.500 |" in md
