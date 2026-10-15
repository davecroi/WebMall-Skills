import json

from webmall_skills.skillopt_webmall.cache import RolloutCache
from webmall_skills.skillopt_webmall.report import eval_records, write_report

BASE = "# base skill\n"
F1 = {"T1": 1.0, "T2": 0.5}


def outcome(tid, f1=None, steps=10):
    f1 = F1.get(tid, 0.0) if f1 is None else f1
    return {"task_id": tid, "f1": f1, "cr": int(f1 == 1.0), "n_steps": steps,
            "input_tokens": 1000, "output_tokens": 100, "env_error": False}


def fake_read(d, tid):
    """Candidate runs: T1 fails, T2 succeeds (opposite of the base skill)."""
    return outcome(tid, f1={"T1": 0.0, "T2": 1.0}[tid], steps=20)


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data) if not isinstance(data, str) else data)


def run_dir_with_runs(tmp_path, history):
    split = tmp_path / "split"
    dump(split / "val" / "items.json", [{"id": "T1", "category": "A"}, {"id": "T2", "category": "B"}])
    dump(split / "train" / "items.json", [{"id": "T3"}, {"id": "T4"}, {"id": "T5"}, {"id": "T6"}])
    dump(tmp_path / "base.md", BASE)
    run = tmp_path / "run"
    dump(run / "config.json", {"split_dir": str(split), "skill_init": str(tmp_path / "base.md"),
                               "val_repeats": 1, "price_input_per_m": 0.1, "price_output_per_m": 0.5,
                               "num_epochs": 2, "batch_size": 2, "gate_metric": "soft"})
    dump(run / "summary.json", {"skillopt": "owned"})
    dump(run / "selection_eval_baseline" / "summary.json", {"soft": 0.75, "hard": 0.5,
                                                             "cost": {"total_usd": 0.1}})
    dump(run / "history.json", history)
    cache = RolloutCache(tmp_path / "cache")
    for tid in ("T1", "T2"):
        base_dir = tmp_path / "old" / f"x_on_webmall.{tid}_0"
        base_dir.mkdir(parents=True)
        cache.put(BASE.strip(), tid, 0, {**outcome(tid), "exp_dir": str(base_dir)})
        cache.put(None, tid, 0, {**outcome(tid, f1=0.0, steps=5), "exp_dir": str(base_dir)})
    for h in history:
        sdir = run / "steps" / f"step_{h['step']:04d}"
        dump(sdir / "candidate_skill.md", BASE + f"- rule {h['step']}\n")
        dump(sdir / "rollout" / "predictions" / "T3" / "outcome.json", outcome("T3", f1=0.0))
        dump(sdir / "rollout" / "summary.json", {"cost": {"total_usd": 0.1 + 0.3 * h["step"]}})
        if h.get("leak"):
            dump(sdir / "selection_eval" / "leakage_report.json", {"hits": ["x"]})
            continue
        for tid in ("T1", "T2"):
            (sdir / "selection_eval" / "agentlab" / "r0" / f"2026_on_webmall.{tid}_0").mkdir(parents=True)
        dump(sdir / "selection_eval" / "summary.json", {"cost": {"total_usd": 0.1 + 0.4 * h["step"]}})
    return run, cache


HISTORY = [
    {"step": 1, "epoch": 1, "action": "accept_new_best", "selection_soft": 0.5, "selection_hard": 0.5,
     "rollout_soft": 0.0, "rollout_n": 1, "n_failure_patches": 1, "n_success_patches": 0,
     "edit_apply_summary": {"applied": 1}, "wall_time_s": 600},
    {"step": 2, "epoch": 1, "action": "reject", "selection_soft": 0.25, "selection_hard": 0.0,
     "rollout_soft": 0.0, "rollout_n": 1, "n_failure_patches": 1, "n_success_patches": 0,
     "edit_apply_summary": {"applied": 2}, "wall_time_s": 1200},
    {"step": 3, "epoch": 2, "action": "reject", "leak": True, "rollout_soft": 0.0, "rollout_n": 1,
     "n_failure_patches": 1, "n_success_patches": 0, "edit_apply_summary": {"applied": 1},
     "wall_time_s": 60},
]


def test_run_summary_timeline_and_three_way_comparison(tmp_path):
    run, cache = run_dir_with_runs(tmp_path, HISTORY)
    md = write_report(run, cache, read_fn=fake_read)
    assert "in progress: 3 of 4 steps done" in md
    assert "| 1 | 1 | 0.000 | 1 / 0 | 1 | 0.500 | 0.500 | -0.250 | accepted ★ | 0.40 | 10 |" in md
    assert "| 2 | 1 | 0.000 | 1 / 0 | 2 | 0.250 | 0.000 | -0.250 | rejected (gate) | 0.40 | 20 |" in md
    assert "| 3 | 2 |" in md and "rejected (test_leakage)" in md and "| — | — | — | rejected (test_leakage) | 0.10 | 1 |" in md
    assert "Best skill: **v0001**" in md and "Caveat" in md
    assert "| best (v0001) | 2 | 0.500 | 0.500 | 0 | 0 |" in md
    assert "| base skill (×1) | 2 | 0.750 | 0.500 | 0 | 0 |" in md
    assert "| no skill (×1) | 2 | 0.000 | 0.000 | 0 | 0 |" in md
    assert "Δ best vs. base" in md and "Δ best vs. no skill" in md
    assert "| T1 | A | 0.000 | 1.000 | 0.000 | -1.000 | 20 | 10 | 5 |" in md
    assert json.loads((run / "summary.json").read_text()) == {"skillopt": "owned"}
    rep = json.loads((run / "report.json").read_text())
    assert rep["best_version"] == "v0001" and len(rep["steps"]) == 3


def test_step_summaries_and_leakage(tmp_path):
    run, cache = run_dir_with_runs(tmp_path, HISTORY)
    write_report(run, cache, read_fn=fake_read)
    s1 = (run / "steps" / "step_0001" / "summary.md").read_text()
    assert "Candidate v0001 vs. parent v0000" in s1
    assert "| T3 | 0.000 | 0 | 10 |" in s1
    assert "| candidate v0001 | 2 | 0.500 |" in s1 and "| parent v0000 | 2 | 0.750 |" in s1
    assert "+- rule 1" in s1
    s2 = (run / "steps" / "step_0002" / "summary.md").read_text()
    assert "parent v0001" in s2 and "--- v0001.md" in s2 and "+- rule 2" in s2
    s3 = (run / "steps" / "step_0003" / "summary.md").read_text()
    assert "No val runs for this step (rejected (test_leakage))" in s3


def test_best_is_base_compares_base_and_no_skill_only(tmp_path):
    history = [{**HISTORY[1], "step": 1}]
    run, cache = run_dir_with_runs(tmp_path, history)
    md = write_report(run, cache, read_fn=fake_read)
    assert "no candidate has beaten the base skill yet, so best = base" in md
    assert "best (v0000)" not in md and "Δ base vs. no skill" in md


def test_eval_records_takes_latest_attempt_per_task(tmp_path):
    r0 = tmp_path / "agentlab" / "r0"
    for name in ("2026-01_on_webmall.T1_0", "2026-02_on_webmall.T1_0", "2026-01_on_webmall.T2_0"):
        (r0 / name).mkdir(parents=True)
    recs = eval_records(tmp_path, read_fn=lambda d, t: {"task_id": t})
    assert set(recs) == {("T1", 0), ("T2", 0)}
    assert recs[("T1", 0)]["exp_dir"].endswith("2026-02_on_webmall.T1_0")


def test_skipped_step_shows_dashes(tmp_path):
    history = [*HISTORY[:1], {"step": 2, "epoch": 1, "action": "skip_no_patches"}]
    run, cache = run_dir_with_runs(tmp_path, HISTORY[:1])
    (run / "history.json").write_text(json.dumps(history))
    md = write_report(run, cache, read_fn=fake_read)
    assert "| 2 | 1 | — | — / — | — | — | — | — | skipped (skip_no_patches) |" in md
