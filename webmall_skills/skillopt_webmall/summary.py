"""Shared helpers for step 0 and C3 run summaries: efficiency metrics (steps, tokens, cost, time) and their markdown tables."""
from __future__ import annotations

import json
from pathlib import Path


def _mean_f1(recs: list) -> float | None:
    return None if not recs or any(r is None for r in recs) else sum(r["f1"] for r in recs) / len(recs)


def _mean_steps(recs: list) -> float | None:
    recs = [r for r in recs if r is not None]
    return sum(r["n_steps"] for r in recs) / len(recs) if recs else None


def _fmt(x: float | None, signed: bool = False) -> str:
    return "—" if x is None else f"{x:+.3f}" if signed else f"{x:.3f}"


def _fmt_steps(x: float | None) -> str:
    return "—" if x is None else f"{x:g}"


def run_seconds(exp_dir) -> float | None:
    """Agent (LLM) + env (browser) seconds of one run, incl. a relaunched first attempt."""
    def secs(d: Path) -> float | None:
        p = Path(d) / "summary_info.json"
        if not p.exists():
            return None
        info = json.loads(p.read_text())
        return (float(info.get("stats.cum_agent_elapsed", 0.0))
                + float(info.get("stats.cum_step_elapsed", 0.0)))
    total = secs(exp_dir)
    marker = Path(exp_dir) / "first_attempt.txt"
    if total is not None and marker.exists():
        total += secs(Path(marker.read_text().strip())) or 0.0
    return total


def efficiency(recs: list, price_in: float, price_out: float, max_steps: int) -> dict:
    """Means per run (successes and failures alike) plus totals; None records are skipped."""
    recs = [r for r in recs if r is not None]
    n = len(recs)
    costs = [(r["input_tokens"] * price_in + r["output_tokens"] * price_out) / 1e6 for r in recs]
    secs = [r.get("seconds") or 0.0 for r in recs]
    mean = (lambda xs: sum(xs) / n if n else 0.0)
    return {
        "n": n,
        "steps": mean([r["n_steps"] for r in recs]),
        "input_tokens": mean([r["input_tokens"] for r in recs]),
        "output_tokens": mean([r["output_tokens"] for r in recs]),
        "cost_usd": mean(costs),
        "seconds": mean(secs),
        "total_cost_usd": sum(costs),
        "total_seconds": sum(secs),
        "step_limit_hits": sum(1 for r in recs if r["n_steps"] >= max_steps),
    }


_EFF_COLS = (("steps", "{:,.1f}"), ("input_tokens", "{:,.0f}"), ("output_tokens", "{:,.0f}"),
             ("cost_usd", "{:,.4f}"), ("seconds", "{:,.0f}"))


def _delta(a: float, b: float, fmt: str) -> str:
    d = fmt.replace("{:", "{:+").format(a - b)
    return f"{d} ({(a - b) / b:+.0%})" if b else d


def render_efficiency(conds: list[tuple[str, dict]], deltas: list[tuple[str, dict, dict]],
                      totals: list[tuple[str, dict]]) -> list[str]:
    """conds: (row label, efficiency); deltas: (label, a, b) rendered as a − b; totals: (name, eff)."""
    row = (lambda label, e: f"| {label} | " + " | ".join(f.format(e[k]) for k, f in _EFF_COLS)
           + f" | {e['step_limit_hits']} |")
    return [
        "## Efficiency", "",
        "Mean per val run (successes and failures alike). Cost = tokens × config prices; "
        "time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the "
        "step limit.", "",
        "| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |",
        "|---|---|---|---|---|---|---|",
        *[row(label, e) for label, e in conds],
        *[f"| {label} | " + " | ".join(_delta(a[k], b[k], f) for k, f in _EFF_COLS)
          + f" | {a['step_limit_hits'] - b['step_limit_hits']:+d} |" for label, a, b in deltas],
        "",
        "Totals: " + "; ".join(
            f"{name} ${e['total_cost_usd']:.2f} / {e['total_seconds']:.0f} s "
            f"({e['total_seconds'] / 60:.0f} min)" for name, e in totals) + ".", "",
    ]
