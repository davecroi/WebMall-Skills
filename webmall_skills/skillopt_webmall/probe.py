"""Step 0: Luna-only val check before training.

Runs Luna + base skill on the val tasks x env.val_repeats (these become the cached
gate baseline) and Luna without skill x 1 (context). Go criteria: env-error share
< 10 % and base-skill mean val F1 < 0.85 (headroom). The summary is written to
webmall_skills/results/skillopt/probe/<split dir name>/ (the v1 split's is probe/split/).

The results folder (skillopt_results/probe/<split>/) gets a copy of summary.md.

    python -m webmall_skills.skillopt_webmall.probe                    # prices from the C3 config
    python -m webmall_skills.skillopt_webmall.probe --overview-only    # no rollouts
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from webmall_skills.paths import PACKAGE_DIR, REPO_ROOT, resolve
from webmall_skills.skillopt_webmall.summary import (  # noqa: F401  (re-exported for callers and tests)
    _fmt, _fmt_steps, _mean_f1, _mean_steps, efficiency, render_efficiency,
    run_seconds,
)

PROBE_DIR = PACKAGE_DIR / "results/skillopt/probe"


def probe_dir(split_dir: str) -> Path:
    return PROBE_DIR / Path(split_dir).name


def summarize(results: list[dict]) -> dict:
    n = len(results)
    return {
        "n": n,
        "f1": sum(r["soft"] for r in results) / n if n else 0.0,
        "cr": sum(r["hard"] for r in results) / n if n else 0.0,
        "error_rate": sum(1 for r in results if r.get("env_error")) / n if n else 0.0,
    }


def cost_since(before: dict, after: dict) -> dict:
    return {k: after[k] - before.get(k, 0) for k in after}


def go_decision(base: dict, max_error_rate: float = 0.10, max_f1: float = 0.85) -> dict:
    reasons = []
    if base["error_rate"] >= max_error_rate:
        reasons.append(f"env-error share {base['error_rate']:.0%} >= {max_error_rate:.0%}")
    if base["f1"] >= max_f1:
        reasons.append(f"base-skill val F1 {base['f1']:.2f} >= {max_f1:.2f} (no headroom)")
    return {"go": not reasons, "reasons": reasons}


def cfg_overrides(price_in: float | None, price_out: float | None, budget: float,
                  ledger: str) -> list[str]:
    """Probe budget/ledger, plus price overrides only when given (else the config's)."""
    opts = [f"env.budget_usd={budget}", f"env.budget_ledger={ledger}"]
    if price_in is not None:
        opts.append(f"env.price_input_per_m={price_in}")
    if price_out is not None:
        opts.append(f"env.price_output_per_m={price_out}")
    return opts


def _source(recs: list, out_dir: Path) -> str:
    if not recs or any(r is None for r in recs):
        return "missing"
    new = [Path(r["exp_dir"]).is_relative_to(out_dir) for r in recs]
    return "new" if all(new) else "cached" if not any(new) else "mixed"


def per_task_rows(task_ids: list[str], categories: dict, base: dict, noskill: dict,
                  n_rep: int, out_dir: Path) -> list[dict]:
    rows = []
    for tid in task_ids:
        b = [base.get((tid, r)) for r in range(n_rep)]
        n = [noskill.get((tid, 0))]
        bf, nf = _mean_f1(b), _mean_f1(n)
        rows.append({"task": tid, "category": categories[tid], "base_f1": bf, "noskill_f1": nf,
                     "delta": None if bf is None or nf is None else bf - nf,
                     "base_steps": _mean_steps(b), "noskill_steps": _mean_steps(n),
                     "base_runs": _source(b, out_dir), "noskill_runs": _source(n, out_dir)})
    return rows


def render_summary(result: dict, split_dir: str, rows: list[dict]) -> str:
    base_key = next(k for k in result if k.startswith("base_skill_x"))
    n_rep = base_key.removeprefix("base_skill_x")
    base, noskill, decision = result[base_key], result["no_skill_x1"], result["decision"]
    lines = [
        f"# Step 0 — Luna val check ({split_dir})", "",
        "| Condition | Rollouts | Mean F1 | Mean CR | Env-error share |",
        "|---|---|---|---|---|",
        f"| base skill (×{n_rep}) | {base['n']} | {base['f1']:.3f} | {base['cr']:.3f} | {base['error_rate']:.0%} |",
        f"| no skill (×1) | {noskill['n']} | {noskill['f1']:.3f} | {noskill['cr']:.3f} | {noskill['error_rate']:.0%} |",
        "", f"**Decision:** {'GO' if decision['go'] else 'NO-GO'}",
        *[f"- {r}" for r in decision["reasons"]], "",
        f"Cost: ${result['cost']['total_usd']:.2f} for {result['cost']['rollouts']} rollouts.", "",
    ]
    if "efficiency" in result:
        b, n = result["efficiency"]["base_skill"], result["efficiency"]["no_skill"]
        lines += render_efficiency([(f"base skill (×{n_rep})", b), ("no skill (×1)", n)],
                                   [("Δ base vs. no skill", b, n)],
                                   [("base skill", b), ("no skill", n)])
    if rows:
        lines += [
            "## Per task", "",
            "F1 per val task; Δ = base − no skill. Runs: `new` = run by this probe, "
            "`cached` = reused from an earlier probe.", "",
            "| Task | Category | Base F1 | No-skill F1 | Δ | Base steps | No-skill steps | Base runs | No-skill runs |",
            "|---|---|---|---|---|---|---|---|---|",
            *[f"| {r['task']} | {r['category']} | {_fmt(r['base_f1'])} | {_fmt(r['noskill_f1'])} | "
              f"{_fmt(r['delta'], signed=True)} | {_fmt_steps(r['base_steps'])} | "
              f"{_fmt_steps(r['noskill_steps'])} | {r['base_runs']} | {r['noskill_runs']} |" for r in rows],
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--price-in", type=float, default=None,
                   help="USD per 1M input tokens; default: env.price_input_per_m in the C3 config")
    p.add_argument("--price-out", type=float, default=None,
                   help="USD per 1M output tokens; default: env.price_output_per_m in the C3 config")
    p.add_argument("--budget", type=float, default=10.0)
    p.add_argument("--overview-only", action="store_true",
                   help="rebuild the per-task tables from the cache and summary.json; no rollouts")
    args = p.parse_args()

    from webmall_skills.skillopt_webmall import train as train_skillopt
    os.chdir(REPO_ROOT)  # SkillOpt resolves skill_init/split_dir/out_root against the cwd
    train_skillopt.configure_env()
    mod = train_skillopt.register()
    from webmall_skills.skillopt_webmall.tasks import results_root
    root = results_root()
    out = root / "probe"
    sys.argv = ["probe", "--config", str(train_skillopt.C3_CONFIG), "--out_root", str(out),
                "--cfg-options", *cfg_overrides(args.price_in, args.price_out, args.budget,
                                                str(root / "probe_ledger.json"))]
    cfg = mod.load_config(mod.parse_args())
    train_skillopt.check_paths(cfg)
    adapter = mod.get_adapter(cfg)
    adapter.setup(cfg)
    base_text = resolve(cfg["skill_init"]).read_text(encoding="utf-8")
    val = adapter.build_eval_env(env_num=0, split="val", seed=42)
    summary_dir = probe_dir(cfg["split_dir"])
    out = out / summary_dir.name
    n_rep = adapter.val_repeats

    if args.overview_only:
        result = json.loads((summary_dir / "summary.json").read_text())
    else:
        before = adapter.budget.spent()  # the probe ledger also holds earlier probes
        base = summarize(adapter.rollout(val, base_text, str(out / "base_skill"), repeats=n_rep))
        noskill = summarize(adapter.rollout(val, "", str(out / "no_skill"), repeats=1))
        decision = go_decision(base)
        result = {f"base_skill_x{n_rep}": base, "no_skill_x1": noskill, "decision": decision,
                  "split_dir": cfg["split_dir"], "cost": cost_since(before, adapter.budget.spent())}

    # cache records carry each run's AgentLab dir (absent only for env-error runs)
    task_ids = [it["id"] for it in val.items]
    base_recs = {(t, r): adapter.cache.get(base_text.strip(), t, r) for t in task_ids for r in range(n_rep)}
    noskill_recs = {(t, 0): adapter.cache.get(None, t, 0) for t in task_ids}
    from webmall_skills.skillopt_webmall.runner import MAX_STEPS
    for rec in [*base_recs.values(), *noskill_recs.values()]:
        if rec is not None:
            rec["seconds"] = run_seconds(rec["exp_dir"])
    prices = (cfg["price_input_per_m"], cfg["price_output_per_m"])
    result["efficiency"] = {
        "base_skill": efficiency(list(base_recs.values()), *prices, MAX_STEPS),
        "no_skill": efficiency(list(noskill_recs.values()), *prices, MAX_STEPS),
    }
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    categories = {it["id"]: it["category"] for it in val.items}
    md = render_summary(result, cfg["split_dir"],
                        per_task_rows(task_ids, categories, base_recs, noskill_recs, n_rep, out))
    (summary_dir / "summary.md").write_text(md)
    (out / "summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
