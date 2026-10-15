"""Cost ledger and hard ceiling for SkillOpt runs on WebMall.

Target tokens come from AgentLab's summary_info.json, optimizer tokens from SkillOpt's
token tracker; both are priced with the configured target-model prices. The ledger is
a JSON file so the pilot and the full run share one ceiling.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


class BudgetExceeded(RuntimeError):
    pass


def optimizer_tokens() -> tuple[int, int]:
    from skillopt.model import get_token_summary

    summary = get_token_summary()
    stages = [v for k, v in summary.items() if k != "_total"]
    return (sum(v.get("prompt_tokens", 0) for v in stages),
            sum(v.get("completion_tokens", 0) for v in stages))


class Budget:
    """Cost ledger with hard ceiling enforcement.

    Not thread-safe: call record_rollout from one thread (the adapter does).
    """
    def __init__(self, ledger_path: Path, ceiling_usd: float, price_input_per_m: float,
                 price_output_per_m: float, default_rollout_usd: float = 0.10,
                 optimizer_tokens_fn=optimizer_tokens):
        self.ledger_path = Path(ledger_path)
        self.ceiling_usd = float(ceiling_usd)
        self.price_in = float(price_input_per_m)
        self.price_out = float(price_output_per_m)
        self.default_rollout_usd = float(default_rollout_usd)
        self._opt_fn = optimizer_tokens_fn
        led = json.loads(self.ledger_path.read_text()) if self.ledger_path.exists() else {}
        self.target_in = int(led.get("target_input_tokens", 0))
        self.target_out = int(led.get("target_output_tokens", 0))
        self.rollouts = int(led.get("rollouts", 0))
        # optimizer tokens from earlier processes; this process adds its tracker on top
        self._opt_base_in = int(led.get("optimizer_input_tokens", 0))
        self._opt_base_out = int(led.get("optimizer_output_tokens", 0))
        # snapshot tracker value at init to detect within-process double-counting
        self._opt_at_init = self._opt_fn()

    def _cost(self, tin: int, tout: int) -> float:
        return (tin * self.price_in + tout * self.price_out) / 1_000_000

    def _optimizer_totals(self) -> tuple[int, int]:
        tin, tout = self._opt_fn()
        init_in, init_out = self._opt_at_init
        return self._opt_base_in + (tin - init_in), self._opt_base_out + (tout - init_out)

    def spent(self) -> dict:
        target = self._cost(self.target_in, self.target_out)
        optimizer = self._cost(*self._optimizer_totals())
        return {"target_usd": target, "optimizer_usd": optimizer,
                "total_usd": target + optimizer, "rollouts": self.rollouts}

    def save(self) -> None:
        oin, oout = self._optimizer_totals()
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.ledger_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps({
            "target_input_tokens": self.target_in,
            "target_output_tokens": self.target_out,
            "rollouts": self.rollouts,
            "optimizer_input_tokens": oin,
            "optimizer_output_tokens": oout,
            "price_input_per_m": self.price_in,
            "price_output_per_m": self.price_out,
            "ceiling_usd": self.ceiling_usd,
            **{k: round(v, 4) for k, v in self.spent().items() if k.endswith("_usd")},
        }, indent=2))
        os.replace(str(tmp_path), str(self.ledger_path))

    def record_rollout(self, input_tokens: int, output_tokens: int) -> None:
        self.target_in += int(input_tokens)
        self.target_out += int(output_tokens)
        self.rollouts += 1
        self.save()

    def check(self, n_rollouts: int) -> None:
        s = self.spent()
        per = s["target_usd"] / self.rollouts if self.rollouts else self.default_rollout_usd
        projected = s["total_usd"] + n_rollouts * per
        if projected > self.ceiling_usd:
            raise BudgetExceeded(
                f"projected ${projected:.2f} (spent ${s['total_usd']:.2f} + {n_rollouts} rollouts "
                f"x ${per:.3f}) exceeds ceiling ${self.ceiling_usd:.2f}"
            )
