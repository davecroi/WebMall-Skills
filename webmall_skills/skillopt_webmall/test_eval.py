"""Held-out test evaluation of one skill on the 33 test tasks of the thesis split.

One skill per call, so the API credit is spent one complete condition at a time:

    python -m webmall_skills.skillopt_webmall.test_eval best --credit 3.78   # credit left now (OpenAI dashboard)
    python -m webmall_skills.skillopt_webmall.test_eval base                  # reuses the ceiling in the ledger
    python -m webmall_skills.skillopt_webmall.test_eval noskill
    python -m webmall_skills.skillopt_webmall.test_eval --summary-only

Same agent, skill injection and settings as the C3 rollouts (runner.run_tasks: Luna,
50 steps, task_seed 0, one env-error relaunch). Before starting, the cost of all missing
tasks is projected from the condition's mean val cost per run x --margin; if that does not
fit under the ceiling the run is refused, so a started condition can finish. Tasks run one
at a time; each result is cached under skillopt_results/test_cache, so an interrupted
condition resumes without paying twice. A safety stop before each task halts if the
next task could exceed the ceiling.

Outputs: AgentLab runs in skillopt_results/test/<condition>/agentlab/, and
skillopt_results/test/summary.md, copied with summary.json to webmall_skills/results/skillopt/test/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from webmall_skills.paths import PACKAGE_DIR, REPO_ROOT, resolve, results_root
from webmall_skills.skillopt_webmall.budget import Budget
from webmall_skills.skillopt_webmall.cache import RolloutCache
from webmall_skills.skillopt_webmall.report import _score_table, _task_table, score, with_seconds
from webmall_skills.skillopt_webmall.summary import _fmt, efficiency, render_efficiency
from webmall_skills.split.make_split import SPLIT_V2_DIR, load_items

SPLIT_DIR = SPLIT_V2_DIR
CONFIG = Path(__file__).resolve().parent / "configs/c3.yaml"  # train.C3_CONFIG (train not imported here)
SUMMARY_DIR = PACKAGE_DIR / "results/skillopt/test"
MAX_STEPS = 50  # skillopt_webmall.runner.MAX_STEPS (not imported: pulls in AgentLab)
DEFAULT_RUN_USD = 0.035  # fallback per-run estimate when a skill has no cached val runs

# condition -> (label, skill file relative to the repo root; None = no skill)
CONDITIONS = {
    "best": ("best (C3 v0007)", "webmall_skills/skills/skillopt/SKILL.md"),
    "base": ("base skill", "webmall_skills/skills/base/SKILL.md"),
    "noskill": ("no skill", None),
}


def config_env(config: Path = CONFIG) -> dict:
    import yaml
    return yaml.safe_load(config.read_text(encoding="utf-8"))["env"]


def prices(config: Path = CONFIG) -> tuple[float, float]:
    env = config_env(config)
    return float(env["price_input_per_m"]), float(env["price_output_per_m"])


def skill_text(cond: str) -> str | None:
    path = CONDITIONS[cond][1]
    return None if path is None else resolve(path).read_text(encoding="utf-8").strip()


def run_cost(rec: dict, price_in: float, price_out: float) -> float:
    return (rec["input_tokens"] * price_in + rec["output_tokens"] * price_out) / 1e6


def per_run_estimate(val_cache: RolloutCache, text: str | None, val_ids: list[str],
                     price_in: float, price_out: float) -> float:
    """Mean val cost per run of this skill (the C3/step 0 cache), else DEFAULT_RUN_USD."""
    recs = [r for t in val_ids if (r := val_cache.get(text, t, 0)) is not None]
    if not recs:
        return DEFAULT_RUN_USD
    return sum(run_cost(r, price_in, price_out) for r in recs) / len(recs)


def ceiling_for(ledger_path: Path, spent: float, credit: float | None) -> float:
    """--credit is the credit left now: ceiling = spent so far + credit; else the stored one."""
    if credit is not None:
        return spent + credit
    led = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    if "ceiling_usd" not in led:
        raise SystemExit("no ceiling recorded yet: pass --credit (USD left on the API key)")
    return float(led["ceiling_usd"])


def check_fits(n_missing: int, per_run: float, margin: float, spent: float,
               ceiling: float) -> tuple[bool, float]:
    projected = n_missing * per_run * margin
    return spent + projected <= ceiling, projected


def run_condition(cond: str, budget: Budget, cache: RolloutCache, items: list[dict],
                  out: Path, per_run: float, margin: float, run_fn=None, outcome_fn=None) -> bool:
    """Run the condition's uncached tasks one at a time. False if the safety stop fired."""
    if run_fn is None:
        from webmall_skills.skillopt_webmall.runner import run_tasks as run_fn
    if outcome_fn is None:
        from webmall_skills.skillopt_webmall.scoring import read_outcome as outcome_fn
    text = skill_text(cond)
    name = "noskill" if text is None else f"test_{cond}"
    todo = [it["id"] for it in items if cache.get(text, it["id"], 0) is None]
    worst = per_run * margin
    for i, tid in enumerate(todo, 1):
        spent = budget.spent()["total_usd"]
        if spent + worst > budget.ceiling_usd:
            print(f"[test_eval] safety stop before {tid}: spent ${spent:.2f} + ${worst:.3f} "
                  f"> ceiling ${budget.ceiling_usd:.2f}; rerun after topping up to resume")
            return False
        dirs = run_fn([tid], text, name, out / "agentlab", 1)
        rec = outcome_fn(dirs[tid], tid)
        rec["exp_dir"] = str(dirs[tid])
        budget.record_rollout(rec["input_tokens"], rec["output_tokens"])
        if rec["env_error"]:
            print(f"[test_eval] {i}/{len(todo)} {tid}: env error (not cached; rerun to retry)")
        else:
            cache.put(text, tid, 0, rec)
            print(f"[test_eval] {i}/{len(todo)} {tid}: F1 {rec['f1']:.2f}, {rec['n_steps']} steps, "
                  f"spent ${budget.spent()['total_usd']:.2f} / ${budget.ceiling_usd:.2f}")
        worst = max(worst, run_cost(rec, budget.price_in, budget.price_out))
    return True


def _category_table(items: list[dict], conds: list[tuple[str, dict]]) -> list[str]:
    cats = list(dict.fromkeys(it["category"] for it in items))
    lines = ["| Category | " + " | ".join(f"{label} F1" for label, _ in conds) + " |",
             "|---|" + "---|" * len(conds)]
    for c in cats:
        ids = {it["id"] for it in items if it["category"] == c}
        cells = []
        for _, recs in conds:
            rs = [r for (t, _), r in recs.items() if t in ids]
            cells.append(_fmt(None if any(r is None for r in rs)
                              else sum(r["f1"] for r in rs) / len(rs)))
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    return lines + [""]


def build_summary(cache: RolloutCache, items: list[dict], price_in: float,
                  price_out: float) -> tuple[str, dict]:
    ids = [it["id"] for it in items]
    recs = {c: {(t, 0): cache.get(skill_text(c), t, 0) for t in ids} for c in CONDITIONS}
    done = [c for c in CONDITIONS if any(v is not None for v in recs[c].values())]
    result = {"n_tasks": len(ids), "conditions": {}}
    lines = ["# Test split — held-out evaluation", "",
             f"{len(ids)} test tasks of `webmall_skills/split/split_v2` (never seen by SkillOpt), "
             "×1 run per skill, Luna, 50 steps. Env errors score 0. Missing = not run yet.", ""]
    if not done:
        return "\n".join(lines + ["No condition has been run yet.", ""]), result
    labelled = [(CONDITIONS[c][0], recs[c]) for c in done]
    scores = [(label, score(r)) for label, r in labelled]
    effs = {c: efficiency(list(with_seconds(recs[c]).values()), price_in, price_out, MAX_STEPS)
            for c in done}
    for c, (_, s) in zip(done, scores):
        result["conditions"][c] = {"label": CONDITIONS[c][0], "skill": CONDITIONS[c][1],
                                   "score": s, "efficiency": effs[c]}
    lines += _score_table(scores)
    lines += ["## Per category", "", *_category_table(items, labelled)]
    pairs = [(a, b) for a, b in (("best", "base"), ("best", "noskill"), ("base", "noskill"))
             if a in done and b in done]
    lines += render_efficiency(
        [(CONDITIONS[c][0], effs[c]) for c in done],
        [(f"Δ {CONDITIONS[a][0]} vs. {CONDITIONS[b][0]}", effs[a], effs[b]) for a, b in pairs],
        [(CONDITIONS[c][0], effs[c]) for c in done],
    )
    lines[lines.index("## Efficiency") + 2] = lines[lines.index("## Efficiency") + 2].replace(
        "per val run", "per test run")
    if len(done) >= 2:
        categories = {it["id"]: it["category"] for it in items}
        lines += ["## Per task", "",
                  f"Δ = {labelled[0][0]} − {labelled[1][0]}.", "",
                  *_task_table(ids, categories, labelled)]
    return "\n".join(lines), result


def write_summary(root: Path, cache: RolloutCache, items: list[dict], price_in: float,
                  price_out: float) -> str:
    md, result = build_summary(cache, items, price_in, price_out)
    (root / "test").mkdir(parents=True, exist_ok=True)
    (root / "test" / "summary.md").write_text(md)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    (SUMMARY_DIR / "summary.md").write_text(md)
    (SUMMARY_DIR / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return md


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("condition", nargs="?", choices=sorted(CONDITIONS))
    p.add_argument("--credit", type=float, default=None,
                   help="USD left on the API key right now; sets the ceiling (stored in the ledger)")
    p.add_argument("--margin", type=float, default=1.25,
                   help="safety factor on the projected cost (test tasks may run longer than val)")
    p.add_argument("--dry-run", action="store_true", help="print the projection, run nothing")
    p.add_argument("--summary-only", action="store_true", help="rebuild the summary, run nothing")
    args = p.parse_args()
    if not args.summary_only and args.condition is None:
        p.error("give a condition (best, base, noskill) or --summary-only")

    root = results_root()
    price_in, price_out = prices()
    items = load_items("test", SPLIT_DIR)
    cache = RolloutCache(root / "test_cache")
    if args.summary_only:
        print(write_summary(root, cache, items, price_in, price_out))
        return

    ledger = root / "test_ledger.json"
    budget = Budget(ledger, 0.0, price_in, price_out, optimizer_tokens_fn=lambda: (0, 0))
    spent = budget.spent()["total_usd"]
    budget.ceiling_usd = ceiling_for(ledger, spent, args.credit)
    text = skill_text(args.condition)
    val_ids = [it["id"] for it in load_items("val", SPLIT_DIR)]
    per_run = per_run_estimate(RolloutCache(root / "rollout_cache"), text, val_ids, price_in, price_out)
    missing = sum(1 for it in items if cache.get(text, it["id"], 0) is None)
    fits, projected = check_fits(missing, per_run, args.margin, spent, budget.ceiling_usd)
    print(f"[test_eval] {args.condition}: {missing}/{len(items)} tasks to run, projected "
          f"${projected:.2f} (${per_run:.4f}/run x {args.margin}); spent ${spent:.2f}, "
          f"ceiling ${budget.ceiling_usd:.2f}, left ${budget.ceiling_usd - spent:.2f}")
    if not fits:
        print("[test_eval] not started: the projected cost does not fit the remaining credit")
        sys.exit(2)
    budget.save()  # stores the ceiling for later calls
    if args.dry_run or not missing:
        print(write_summary(root, cache, items, price_in, price_out) if not missing else "")
        return

    from webmall_skills.skillopt_webmall import train as train_skillopt
    os.chdir(REPO_ROOT)  # SkillOpt resolves skill_init/split_dir/out_root against the cwd
    train_skillopt.configure_env()
    train_skillopt.check_paths(config_env())
    finished = run_condition(args.condition, budget, cache, items, root / "test" / args.condition,
                             per_run, args.margin)
    print(write_summary(root, cache, items, price_in, price_out))
    sys.exit(0 if finished else 3)


if __name__ == "__main__":
    main()
