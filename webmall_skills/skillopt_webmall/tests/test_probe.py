import json

from webmall_skills.skillopt_webmall.probe import go_decision, summarize


def r(soft, hard=0, env_error=False):
    return {"soft": soft, "hard": hard, "env_error": env_error}


def test_summarize():
    s = summarize([r(1.0, 1), r(0.5), r(0.0, env_error=True), r(0.5)])
    assert s == {"n": 4, "f1": 0.5, "cr": 0.25, "error_rate": 0.25}


def test_go_when_stable_with_headroom():
    assert go_decision({"n": 22, "f1": 0.5, "cr": 0.3, "error_rate": 0.05})["go"] is True


def test_no_go_on_errors_or_ceiling():
    d = go_decision({"n": 22, "f1": 0.9, "cr": 0.8, "error_rate": 0.2})
    assert d["go"] is False and len(d["reasons"]) == 2


def test_probe_dir_is_named_after_the_split():
    from webmall_skills.skillopt_webmall.probe import PROBE_DIR, probe_dir
    assert probe_dir("webmall_skills/split/split_v2") == PROBE_DIR / "split_v2"


def test_cost_since_reports_only_this_probe():
    from webmall_skills.skillopt_webmall.probe import cost_since
    before = {"total_usd": 0.88, "rollouts": 33}
    assert cost_since(before, {"total_usd": 1.5, "rollouts": 64}) == {"total_usd": 1.5 - 0.88, "rollouts": 31}


def rec(f1, exp_dir, n_steps=10):
    return {"f1": f1, "exp_dir": str(exp_dir), "n_steps": n_steps}


def test_per_task_rows_and_table(tmp_path):
    from webmall_skills.skillopt_webmall.probe import per_task_rows, render_summary
    out = tmp_path / "probe" / "split_v2"
    base = {("T1", 0): rec(1.0, out / "base_skill" / "agentlab" / "r0" / "x", n_steps=30),
            ("T2", 0): rec(0.5, tmp_path / "probe" / "base_skill" / "agentlab" / "r0" / "y")}
    noskill = {("T1", 0): rec(0.5, tmp_path / "old"), ("T2", 0): None}
    rows = per_task_rows(["T1", "T2"], {"T1": "Cat_A", "T2": "Cat_B"}, base, noskill, 1, out)
    assert rows[0] == {"task": "T1", "category": "Cat_A", "base_f1": 1.0, "noskill_f1": 0.5,
                       "delta": 0.5, "base_steps": 30, "noskill_steps": 10,
                       "base_runs": "new", "noskill_runs": "cached"}
    assert rows[1]["noskill_f1"] is None and rows[1]["delta"] is None
    assert rows[1]["base_runs"] == "cached" and rows[1]["noskill_runs"] == "missing"
    result = {"base_skill_x1": {"n": 2, "f1": 0.75, "cr": 0.5, "error_rate": 0.0},
              "no_skill_x1": {"n": 2, "f1": 0.5, "cr": 0.0, "error_rate": 0.0},
              "decision": {"go": True, "reasons": []},
              "cost": {"total_usd": 0.62, "rollouts": 20}}
    md = render_summary(result, "webmall_skills/split/split_v2", rows)
    assert "| base skill (×1) | 2 | 0.750 |" in md and "**Decision:** GO" in md
    assert "| T1 | Cat_A | 1.000 | 0.500 | +0.500 | 30 | 10 | new | cached |" in md
    assert "| T2 | Cat_B | 0.500 | — | — | 10 | — | cached | missing |" in md
    assert "## Efficiency" not in md


def test_cfg_overrides_use_config_prices_unless_given():
    from webmall_skills.skillopt_webmall.probe import cfg_overrides
    assert cfg_overrides(None, None, 10.0, "l.json") == ["env.budget_usd=10.0", "env.budget_ledger=l.json"]
    assert cfg_overrides(0.1, 0.5, 10.0, "l.json") == [
        "env.budget_usd=10.0", "env.budget_ledger=l.json",
        "env.price_input_per_m=0.1", "env.price_output_per_m=0.5"]
    assert cfg_overrides(0.2, None, 10.0, "l.json")[-1] == "env.price_input_per_m=0.2"


def test_run_seconds_adds_relaunched_first_attempt(tmp_path):
    from webmall_skills.skillopt_webmall.probe import run_seconds
    first, run = tmp_path / "first", tmp_path / "run"
    for d, agent, step in ((first, 10.0, 5.0), (run, 100.0, 20.0)):
        d.mkdir()
        (d / "summary_info.json").write_text(json.dumps(
            {"stats.cum_agent_elapsed": agent, "stats.cum_step_elapsed": step}))
    assert run_seconds(run) == 120.0
    (run / "first_attempt.txt").write_text(str(first))
    assert run_seconds(run) == 135.0
    assert run_seconds(tmp_path / "missing") is None


def eff_rec(steps, tin, tout, seconds):
    return {"n_steps": steps, "input_tokens": tin, "output_tokens": tout, "seconds": seconds}


def test_efficiency_means_totals_and_step_limit():
    from webmall_skills.skillopt_webmall.probe import efficiency
    e = efficiency([eff_rec(50, 1_000_000, 10_000, 300.0), eff_rec(10, 0, 0, 100.0), None],
                   price_in=0.10, price_out=0.50, max_steps=50)
    assert e["n"] == 2 and e["step_limit_hits"] == 1
    assert e["steps"] == 30 and e["input_tokens"] == 500_000 and e["output_tokens"] == 5_000
    assert abs(e["total_cost_usd"] - 0.105) < 1e-9 and abs(e["cost_usd"] - 0.0525) < 1e-9
    assert e["seconds"] == 200.0 and e["total_seconds"] == 400.0


def test_summary_renders_efficiency_with_delta():
    from webmall_skills.skillopt_webmall.probe import render_summary
    eff = {"n": 2, "steps": 30.0, "input_tokens": 500_000.0, "output_tokens": 5_000.0,
           "cost_usd": 0.05, "seconds": 200.0, "total_cost_usd": 0.10, "total_seconds": 400.0,
           "step_limit_hits": 1}
    half = {**eff, "steps": 15.0, "input_tokens": 250_000.0, "output_tokens": 2_500.0,
            "cost_usd": 0.025, "seconds": 100.0, "total_cost_usd": 0.05, "total_seconds": 200.0,
            "step_limit_hits": 0}
    result = {"base_skill_x1": {"n": 2, "f1": 0.75, "cr": 0.5, "error_rate": 0.0},
              "no_skill_x1": {"n": 2, "f1": 0.5, "cr": 0.0, "error_rate": 0.0},
              "decision": {"go": True, "reasons": []},
              "cost": {"total_usd": 0.62, "rollouts": 20},
              "efficiency": {"base_skill": eff, "no_skill": half}}
    md = render_summary(result, "webmall_skills/split/split_v2", [])
    assert "## Efficiency" in md
    assert "| base skill (×1) | 30.0 | 500,000 | 5,000 | 0.0500 | 200 | 1 |" in md
    assert "| no skill (×1) | 15.0 | 250,000 | 2,500 | 0.0250 | 100 | 0 |" in md
    assert "| Δ base vs. no skill | +15.0 (+100%) | +250,000 (+100%) | +2,500 (+100%) | +0.0250 (+100%) | +100 (+100%) | +1 |" in md
    assert "Totals: base skill $0.10 / 400 s (7 min); no skill $0.05 / 200 s (3 min)." in md
