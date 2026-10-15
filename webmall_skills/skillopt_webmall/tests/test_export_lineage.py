import json

from webmall_skills.skillopt_webmall.export_lineage import build_rows, export

BASE = "# Skill\n\n- rule one\n"
V1 = BASE + "- rule two\n"
V2 = V1 + "- rule three\n"
V3 = V1 + "- see /product/secret/\n"


def make_run(tmp_path):
    run = tmp_path / "run"
    (run / "selection_eval_baseline").mkdir(parents=True)
    (run / "selection_eval_baseline" / "summary.json").write_text(json.dumps(
        {"n": 22, "hard": 0.2, "soft": 0.40, "webmall": {"avg_f1_score": 0.41}}))
    steps = [
        (1, "accept_new_best", V1, 0.50, 0.30, None),
        (2, "reject", V2, 0.45, 0.25, None),
        (3, "reject", V3, 0.0, 0.0, {"hits": ["answer slug: secret"]}),
    ]
    history = []
    current = 0.40
    for step, action, text, soft, hard, leak in steps:
        d = run / "steps" / f"step_{step:04d}"
        (d / "selection_eval").mkdir(parents=True)
        (d / "candidate_skill.md").write_text(text)
        (d / "ranked_edits.json").write_text(json.dumps(
            {"edits": [{"op": "append", "content": text.splitlines()[-1]}]}))
        (d / "selection_eval" / "summary.json").write_text(json.dumps(
            {"n": 22, "hard": hard, "soft": soft, "webmall": {"avg_f1_score": soft}}))
        if leak:
            (d / "selection_eval" / "leakage_report.json").write_text(json.dumps(leak))
        if action == "accept_new_best":
            current = soft
        history.append({"step": step, "epoch": step, "action": action,
                        "selection_hard": hard, "selection_soft": soft, "current_score": current})
    history.append({"step": 4, "epoch": 4, "action": "skip_no_patches", "current_score": current})
    (run / "history.json").write_text(json.dumps(history))
    (run / "best_skill.md").write_text(V1)
    (run / "config.json").write_text(json.dumps({"split_dir": "webmall_skills/split/split_v2"}))
    base = tmp_path / "base.md"
    base.write_text(BASE)
    return run, base


def test_rows(tmp_path):
    run, _ = make_run(tmp_path)
    rows = build_rows(run)
    assert [r["version"] for r in rows] == ["v0000", "v0001", "v0002", "v0003", "v0004"]
    assert [r["decision"] for r in rows] == [
        "seed", "accepted", "rejected (gate)", "rejected (test_leakage)", "skipped (skip_no_patches)"]
    assert [r["parent"] for r in rows] == ["", "v0000", "v0001", "v0001", "v0001"]
    assert [r["best"] for r in rows] == [True, True, False, False, False]
    assert rows[1]["f1_before"] == 0.40 and rows[1]["f1_after"] == 0.50
    assert rows[2]["f1_before"] == 0.50
    assert rows[3]["f1_after"] is None


def test_export_files_and_determinism(tmp_path):
    run, base = make_run(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    export(run, a, base, None)
    export(run, b, base, None)
    assert (a / "SKILL.md").read_text() == V1
    assert (a / "history" / "v0000_base.md").read_text() == BASE
    assert (a / "history" / "v0003.md").read_text() == V3
    assert "+- rule three" in (a / "history" / "v0002.diff").read_text()
    assert (a / "history" / "v0002.edits.json").exists()
    assert not (a / "history" / "v0004.md").exists()
    table = (a / "HISTORY.md").read_text()
    assert "rejected (test_leakage)" in table and "★" in table and "Env errors" in table
    assert (a / "run" / "history.json").exists() and (a / "README.md").exists()
    files_a = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    assert files_a == files_b
    assert all((a / f).read_bytes() == (b / f).read_bytes() for f in files_a)


def test_export_copies_report_summary_and_names_val_setup(tmp_path):
    run, base = make_run(tmp_path)
    (run / "config.json").write_text(json.dumps({"split_dir": "webmall_skills/split/split_v2", "val_repeats": 1}))
    export(run, tmp_path / "a", base, None)
    assert not (tmp_path / "a" / "SUMMARY.md").exists()
    assert "21 val tasks × 1 repeat (the gate score)" in (tmp_path / "a" / "HISTORY.md").read_text()
    (run / "summary.md").write_text("# C3 run summary\n")
    export(run, tmp_path / "a", base, None)
    assert (tmp_path / "a" / "SUMMARY.md").read_text() == "# C3 run summary\n"
