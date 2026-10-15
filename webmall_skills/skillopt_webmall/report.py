"""Summaries of a C3 SkillOpt run.

    python -m webmall_skills.skillopt_webmall.report RUN_DIR      # e.g. skillopt_results/c3_full

Writes RUN_DIR/summary.md (+ report.json; SkillOpt owns summary.json): step timeline,
and the best skill vs. the base skill vs. no skill on val (F1/CR, efficiency, per task). Writes
steps/step_NNNN/summary.md per completed step: train outcomes, candidate vs. the skill
it tried to replace on val and the skill diff. Read-only on the run except for these files, so it can be run while
training is still in progress (steps without a history entry are skipped).
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
from pathlib import Path

from webmall_skills.skillopt_webmall.cache import RolloutCache
from webmall_skills.skillopt_webmall.export_lineage import build_rows
from webmall_skills.skillopt_webmall.summary import (
    _fmt, _fmt_steps, _mean_f1, _mean_steps, efficiency, render_efficiency,
    run_seconds,
)
from webmall_skills.paths import resolve, results_root

MAX_STEPS = 50  # skillopt_webmall.runner.MAX_STEPS (not imported: pulls in AgentLab)

CAVEAT = ("**Caveat:** the best skill was *selected* on these val tasks, so its val score "
          "is optimistic. The unbiased comparison is the test split "
          "(`webmall_skills_test` in `run_webmall_study.py`, or "
          "`python -m webmall_skills.skillopt_webmall.test_eval`), run once per skill.")


def _read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else None


def _task_of(run_dir_name: str) -> str:
    """'…_on_webmall.Webmall_Checkout_Task6_0' -> 'Webmall_Checkout_Task6'."""
    return run_dir_name.split("_on_webmall.", 1)[1].rsplit("_", 1)[0]


def eval_records(eval_dir: Path, read_fn=None) -> dict:
    """{(task_id, repeat): outcome + exp_dir} from eval_dir/agentlab/r*/ (latest run per task)."""
    if read_fn is None:
        from webmall_skills.skillopt_webmall.scoring import read_outcome as read_fn
    records: dict = {}
    for rdir in sorted(Path(eval_dir).glob("agentlab/r*")):
        r = int(rdir.name[1:])
        latest: dict[str, Path] = {}
        for d in sorted(p for p in rdir.iterdir() if p.is_dir() and "_on_webmall." in p.name):
            latest[_task_of(d.name)] = d  # names start with a timestamp: last = latest attempt
        for tid, d in latest.items():
            records[(tid, r)] = {**read_fn(d, tid), "exp_dir": str(d)}
    return records


def cache_records(cache: RolloutCache, skill_text: str | None, task_ids, n_rep: int) -> dict:
    text = (skill_text or "").strip() or None
    return {(t, r): cache.get(text, t, r) for t in task_ids for r in range(n_rep)}


def train_records(rollout_dir: Path) -> dict:
    return {p.parent.name: _read_json(p)
            for p in sorted(Path(rollout_dir).glob("predictions/*/outcome.json"))}


def score(records: dict) -> dict:
    """Mean F1/CR over present records; env errors score 0 like the gate; missing are counted."""
    present = [r for r in records.values() if r is not None]
    n = len(present)
    return {"n": n, "missing": len(records) - n,
            "f1": sum(r["f1"] for r in present) / n if n else 0.0,
            "cr": sum(r["cr"] for r in present) / n if n else 0.0,
            "env_errors": sum(1 for r in present if r.get("env_error"))}


def with_seconds(records: dict) -> dict:
    for rec in records.values():
        if rec is not None and "seconds" not in rec:
            rec["seconds"] = run_seconds(rec["exp_dir"])
    return records


def _eff(records: dict, cfg: dict) -> dict:
    return efficiency(list(with_seconds(records).values()), cfg["price_input_per_m"],
                      cfg["price_output_per_m"], MAX_STEPS)


def _v(x) -> str:
    return "—" if x is None else str(x)


def _money(x: float | None) -> str:
    return "—" if x is None else f"{x:.2f}"


def _score_table(conds: list[tuple[str, dict]]) -> list[str]:
    return [
        "| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |",
        "|---|---|---|---|---|---|",
        *[f"| {label} | {s['n']} | {s['f1']:.3f} | {s['cr']:.3f} | {s['env_errors']} | {s['missing']} |"
          for label, s in conds],
        "",
    ]


def _task_table(task_ids, categories, conds: list[tuple[str, dict]]) -> list[str]:
    """Per task: F1 of every condition (mean over its repeats), Δ first − second, steps."""
    names = [label for label, _ in conds]
    lines = ["| Task | Category | " + " | ".join(f"{n} F1" for n in names)
             + f" | Δ {names[0]} − {names[1]} | " + " | ".join(f"{n} steps" for n in names) + " |",
             "|---|---|" + "---|" * (2 * len(names) + 1)]
    for t in task_ids:
        recs = [[v for (tt, _), v in c.items() if tt == t] for _, c in conds]
        f1s = [_mean_f1(rs) for rs in recs]
        delta = None if f1s[0] is None or f1s[1] is None else f1s[0] - f1s[1]
        lines.append(f"| {t} | {categories[t]} | " + " | ".join(_fmt(f) for f in f1s)
                     + f" | {_fmt(delta, signed=True)} | "
                     + " | ".join(_fmt_steps(_mean_steps(rs)) for rs in recs) + " |")
    return lines + [""]


def _val_tasks(cfg: dict) -> tuple[list[str], dict]:
    items = _read_json(resolve(cfg["split_dir"]) / "val" / "items.json")
    return [it["id"] for it in items], {it["id"]: it["category"] for it in items}


def _version_text(run_dir: Path, version: str, base_text: str) -> str:
    if version == "v0000":
        return base_text
    return (run_dir / "steps" / f"step_{int(version[1:]):04d}" / "candidate_skill.md").read_text(
        encoding="utf-8")


def _cost_at(run_dir: Path, step: int) -> float | None:
    sdir = (run_dir / "selection_eval_baseline" if step == 0
            else run_dir / "steps" / f"step_{step:04d}")
    for sub in ((".",) if step == 0 else ("selection_eval", "rollout")):
        s = _read_json(sdir / sub / "summary.json")
        if s and "cost" in s:
            return s["cost"]["total_usd"]
    return None


def build_report(run_dir: Path, cache: RolloutCache, read_fn=None) -> dict:
    """Everything both summaries need, as plain data (also written as report.json)."""
    run_dir = Path(run_dir)
    cfg = _read_json(run_dir / "config.json")
    history = {h["step"]: h for h in _read_json(run_dir / "history.json") or []}
    rows = {r["version"]: r for r in build_rows(run_dir)}
    n_rep = int(cfg.get("val_repeats", 1))
    task_ids, categories = _val_tasks(cfg)
    base_text = resolve(cfg["skill_init"]).read_text(encoding="utf-8")

    base = cache_records(cache, base_text, task_ids, n_rep)
    noskill = cache_records(cache, None, task_ids, 1)
    val_by_version = {"v0000": base}
    steps, prev_cost = [], _cost_at(run_dir, 0)
    for step in sorted(history):
        h, ver = history[step], f"v{step:04d}"
        row, sdir = rows[ver], run_dir / "steps" / f"step_{step:04d}"
        cand = (eval_records(sdir / "selection_eval", read_fn)
                if row["f1_after"] is not None else {})
        val_by_version[ver] = cand
        cost = _cost_at(run_dir, step)
        steps.append({
            "step": step, "version": ver, "epoch": h.get("epoch"), "parent": row["parent"],
            "decision": row["decision"], "best": row["best"],
            "train_f1": h.get("rollout_soft"), "train_n": h.get("rollout_n"),
            "failure_patches": h.get("n_failure_patches"), "success_patches": h.get("n_success_patches"),
            "edits_applied": (h.get("edit_apply_summary") or {}).get("applied"),
            "val_f1": row["f1_after"], "val_cr": row["cr"], "parent_f1": row["f1_before"],
            "cost_usd": None if cost is None or prev_cost is None else cost - prev_cost,
            "wall_s": h.get("wall_time_s"),
            "train": train_records(sdir / "rollout"), "val": cand,
        })
        prev_cost = cost if cost is not None else prev_cost

    best_ver = [v for v, r in rows.items() if r["best"]][-1]
    planned = int(cfg.get("num_epochs", 1)) * math.ceil(
        len(_read_json(resolve(cfg["split_dir"]) / "train" / "items.json"))
        / int(cfg.get("batch_size", 1)))
    return {"run_dir": str(run_dir), "cfg": cfg, "n_rep": n_rep, "task_ids": task_ids,
            "categories": categories, "base_text": base_text, "steps": steps,
            "planned_steps": planned, "best_version": best_ver,
            "val": {"best": val_by_version[best_ver], "base": base, "noskill": noskill},
            "val_by_version": val_by_version}


def render_run(rep: dict) -> str:
    cfg, n_rep, steps = rep["cfg"], rep["n_rep"], rep["steps"]
    best, base, noskill = rep["val"]["best"], rep["val"]["base"], rep["val"]["noskill"]
    best_label = f"best ({rep['best_version']})"
    best_is_base = rep["best_version"] == "v0000"
    done = len(steps)
    status = ("finished" if done >= rep["planned_steps"]
              else f"in progress: {done} of {rep['planned_steps']} steps done")
    lines = [
        f"# C3 run summary — {Path(rep['run_dir']).name}", "",
        f"Split `{cfg['split_dir']}`, {len(rep['task_ids'])} val tasks × {n_rep}, "
        f"{cfg.get('num_epochs')} epochs, gate `{cfg.get('gate_metric')}` (mean per-task F1). "
        f"Status: **{status}**.", "",
        "## Steps", "",
        "Train F1 = mean over the step's train batch; patches = minibatches the optimizer "
        "reflected on (failure / success); Δ = candidate val F1 − val F1 of the skill it "
        "tried to replace.", "",
        "| Step | Epoch | Train F1 | Patches (fail / succ) | Edits | Cand. val F1 | Cand. val CR | Δ | Decision | Cost ($) | Time (min) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in steps:
        delta = (None if s["val_f1"] is None or s["parent_f1"] is None
                 else s["val_f1"] - s["parent_f1"])
        lines.append(
            f"| {s['step']} | {s['epoch']} | {_fmt(s['train_f1'])} | "
            f"{_v(s['failure_patches'])} / {_v(s['success_patches'])} | {_v(s['edits_applied'])} | "
            f"{_fmt(s['val_f1'])} | {_fmt(s['val_cr'])} | {_fmt(delta, signed=True)} | "
            f"{s['decision']}{' ★' if s['best'] else ''} | {_money(s['cost_usd'])} | "
            f"{'—' if s['wall_s'] is None else round(s['wall_s'] / 60)} |")
    costs = [s["cost_usd"] for s in steps if s["cost_usd"] is not None]
    lines += ["", f"Training cost so far: ${sum(costs):.2f} over {done} steps "
                  f"(base-skill baseline came from the step 0 cache).", ""]

    lines += ["## Best skill vs. base skill vs. no skill (val)", "",
              f"Best skill: **{rep['best_version']}**"
              + ((" — no candidate has beaten the base skill"
                  + (" yet" if done < rep["planned_steps"] else "") + ", so best = base.")
                 if best_is_base
                 else f" (`steps/step_{int(rep['best_version'][1:]):04d}/candidate_skill.md`)."),
              "", CAVEAT, ""]
    eb, ea, en = _eff(best, cfg), _eff(base, cfg), _eff(noskill, cfg)
    base_label = f"base skill (×{n_rep})"
    if best_is_base:  # best = base: compare base vs. no skill only
        lines += _score_table([(base_label, score(base)), ("no skill (×1)", score(noskill))])
        lines += render_efficiency([(base_label, ea), ("no skill (×1)", en)],
                                   [("Δ base vs. no skill", ea, en)],
                                   [("base skill", ea), ("no skill", en)])
    else:
        lines += _score_table([(best_label, score(best)), (base_label, score(base)),
                               ("no skill (×1)", score(noskill))])
        lines += render_efficiency(
            [(best_label, eb), (base_label, ea), ("no skill (×1)", en)],
            [("Δ best vs. base", eb, ea), ("Δ best vs. no skill", eb, en)],
            [("best", eb), ("base skill", ea), ("no skill", en)])
    lines += ["## Per task", "", "F1 and steps per val task (mean over repeats); Δ = "
              + ("base − no skill." if best_is_base else "best − base."), ""]
    lines += _task_table(rep["task_ids"], rep["categories"],
                         [*([("best", best)] if not best_is_base else []),
                          ("base", base), ("no skill", noskill)])
    return "\n".join(lines)


def render_step(rep: dict, s: dict, run_dir: Path) -> str:
    cfg, n_rep = rep["cfg"], rep["n_rep"]
    parent = rep["val_by_version"].get(s["parent"], {})
    lines = [
        f"# Step {s['step']} (epoch {s['epoch']}) — {s['decision']}{' ★' if s['best'] else ''}", "",
        f"Candidate {s['version']} vs. parent {s['parent']}: val F1 {_fmt(s['val_f1'])} vs. "
        f"{_fmt(s['parent_f1'])}; {s['edits_applied']} edits applied from "
        f"{s['failure_patches']} failure / {s['success_patches']} success patches.", "",
        "## Train batch", "",
        "| Task | F1 | CR | Steps |", "|---|---|---|---|",
        *[f"| {t} | {_fmt(o['f1'])} | {o['cr']} | {o['n_steps']} |"
          for t, o in s["train"].items() if o is not None],
        "",
    ]
    if s["val"]:
        lines += ["## Val: candidate vs. parent", ""]
        lines += _score_table([(f"candidate {s['version']}", score(s["val"])),
                               (f"parent {s['parent']}", score(parent))])
        ec, ep = _eff(s["val"], cfg), _eff(parent, cfg)
        lines += render_efficiency([(f"candidate {s['version']}", ec), (f"parent {s['parent']}", ep)],
                                   [("Δ candidate vs. parent", ec, ep)],
                                   [("candidate", ec), ("parent", ep)])
        lines += ["## Per task", "", "Δ = candidate − parent.", ""]
        lines += _task_table(rep["task_ids"], rep["categories"],
                             [("candidate", s["val"]), ("parent", parent)])
    else:
        lines += ["No val runs for this step (" + s["decision"] + ").", ""]
    sdir = run_dir / "steps" / f"step_{s['step']:04d}"
    if (sdir / "candidate_skill.md").exists():
        diff = difflib.unified_diff(
            _version_text(run_dir, s["parent"], rep["base_text"]).splitlines(keepends=True),
            (sdir / "candidate_skill.md").read_text(encoding="utf-8").splitlines(keepends=True),
            fromfile=f"{s['parent']}.md", tofile=f"{s['version']}.md")
        lines += ["## Skill diff (parent → candidate)", "", "```diff", "".join(diff).rstrip(), "```", ""]
    return "\n".join(lines)


def _jsonable(rep: dict) -> dict:
    def recs(d):
        return {f"{t}@r{r}": v for (t, r), v in d.items()}
    return {
        "best_version": rep["best_version"], "planned_steps": rep["planned_steps"],
        "steps": [{k: v for k, v in s.items() if k not in ("train", "val")} for s in rep["steps"]],
        "val": {k: {"score": score(v), "efficiency": _eff(v, rep["cfg"])} for k, v in rep["val"].items()},
        "val_records": {k: recs(v) for k, v in rep["val"].items()},
    }


def write_report(run_dir: Path, cache: RolloutCache, read_fn=None) -> str:
    run_dir = Path(run_dir)
    rep = build_report(run_dir, cache, read_fn)
    for s in rep["steps"]:
        sdir = run_dir / "steps" / f"step_{s['step']:04d}"
        if not sdir.is_dir():  # e.g. a skipped step SkillOpt left no folder for
            continue
        (sdir / "summary.md").write_text(render_step(rep, s, run_dir), encoding="utf-8")
    md = render_run(rep)
    (run_dir / "summary.md").write_text(md, encoding="utf-8")
    (run_dir / "report.json").write_text(json.dumps(_jsonable(rep), indent=2, default=str) + "\n")
    return md


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir", type=Path)
    p.add_argument("--cache", type=Path, default=None, help="default: <results root>/rollout_cache")
    args = p.parse_args()
    print(write_report(args.run_dir, RolloutCache(args.cache or results_root() / "rollout_cache")))


if __name__ == "__main__":
    main()
