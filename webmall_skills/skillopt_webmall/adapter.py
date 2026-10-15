"""SkillOpt EnvAdapter for WebMall. See the C3 design spec."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from webmall_skills.paths import resolve, results_root
from webmall_skills.skillopt_webmall import scoring, trajectory
from webmall_skills.skillopt_webmall.budget import Budget
from webmall_skills.skillopt_webmall.cache import RolloutCache
from webmall_skills.skillopt_webmall.dataloader import WebMallDataLoader
from webmall_skills.skillopt_webmall.leakage import build_test_blocklist, leakage_hits
from webmall_skills.skillopt_webmall.tasks import load_task_index

_SPLIT = {"train": "train", "valid_seen": "val", "selection": "val", "val": "val",
          "valid_unseen": "test", "test": "test"}


@dataclass
class WebMallBatch:
    split: str
    items: list[dict] = field(default_factory=list)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class WebMallAdapter(EnvAdapter):
    def __init__(self, split_dir: str = "", split_mode: str = "split_dir", split_seed: int = 42,
                 seed: int = 42, limit: int = 0, analyst_workers: int = 4,
                 failure_only: bool = False, minibatch_size: int = 4, edit_budget: int = 4,
                 val_repeats: int = 2, budget_usd: float = 25.0, budget_ledger: str = "",
                 price_input_per_m: float | None = None, price_output_per_m: float | None = None,
                 n_jobs: int = 1, cache_dir: str = "", run_fn=None, outcome_fn=None,
                 steps_fn=None) -> None:
        if price_input_per_m is None or price_output_per_m is None:
            raise ValueError("set env.price_input_per_m and env.price_output_per_m "
                             "(USD per 1M tokens of the target model) in the config")
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.val_repeats = int(val_repeats)
        self.n_jobs = int(n_jobs)
        # resolved against the repo root: the loader would otherwise join it with the cwd
        self.dataloader = WebMallDataLoader(split_dir=str(resolve(split_dir)), split_mode=split_mode,
                                            split_seed=split_seed, seed=seed, limit=limit)
        self.blocklist = build_test_blocklist(resolve(split_dir))
        root = results_root()
        self.cache = RolloutCache(Path(cache_dir) if cache_dir else root / "rollout_cache")
        self.budget = Budget(Path(budget_ledger) if budget_ledger else root / "c3_ledger.json",
                             budget_usd, price_input_per_m, price_output_per_m)
        if run_fn is None:
            from webmall_skills.skillopt_webmall.runner import run_tasks as run_fn
        self.run_fn = run_fn
        self.outcome_fn = outcome_fn or scoring.read_outcome
        self.steps_fn = steps_fn or trajectory.load_steps
        self.task_index = load_task_index()

    # ── SkillOpt lifecycle ───────────────────────────────────────────────
    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return WebMallBatch(batch.split, list(batch.payload or []))

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        return self.build_env_from_batch(
            self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs))

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        return self.build_env_from_batch(
            self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs))

    def get_task_types(self) -> list[str]:
        return sorted({t["category"] for t in self.task_index.values()})

    # ── Rollout ──────────────────────────────────────────────────────────
    def rollout(self, env_manager, skill_content: str, out_dir: str,
                repeats: int | None = None, **kwargs) -> list[dict]:
        try:
            return self._rollout(env_manager, skill_content, out_dir, repeats)
        finally:
            self.budget.save()  # persists optimizer tokens on every path, incl. rejects/cache hits

    def _rollout(self, env_manager, skill_content: str, out_dir: str,
                 repeats: int | None) -> list[dict]:
        batch: WebMallBatch = env_manager
        split = _SPLIT.get(batch.split, batch.split)
        if split == "test":
            raise RuntimeError("the test split must not be rolled out during training")
        skill_text = (skill_content or "").strip() or None
        n_rep = repeats if repeats is not None else (self.val_repeats if split == "val" else 1)
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        if split == "val" and skill_text:
            hits = leakage_hits(skill_text, self.blocklist)
            if hits:
                (out / "leakage_report.json").write_text(json.dumps({"hits": hits}, indent=2))
                results = [self._result(it, r, n_rep, None) for it in batch.items for r in range(n_rep)]
                self._write_summary(out, results, [])
                return results

        records: dict[tuple[str, int], dict] = {}
        missing: dict[int, list[str]] = {}
        for it in batch.items:
            for r in range(n_rep):
                rec = self.cache.get(skill_text, it["id"], r) if split == "val" else None
                if rec is None:
                    missing.setdefault(r, []).append(it["id"])
                else:
                    records[(it["id"], r)] = rec
        n_missing = sum(len(v) for v in missing.values())
        if n_missing:
            # a train step also pays for the validation that follows it
            reserve = len(self.dataloader.val_items) * self.val_repeats if split == "train" else 0
            self.budget.check(n_missing + reserve)
        skill_name = "noskill" if not skill_text else "so" + hashlib.sha256(
            skill_text.encode("utf-8")).hexdigest()[:8]
        for r, task_ids in sorted(missing.items()):
            dirs = self.run_fn(task_ids, skill_text, skill_name, out / "agentlab" / f"r{r}", self.n_jobs)
            for tid in task_ids:
                rec = self.outcome_fn(dirs[tid], tid)
                rec["exp_dir"] = str(dirs[tid])
                self.budget.record_rollout(rec["input_tokens"], rec["output_tokens"])
                if split == "val" and not rec["env_error"]:
                    self.cache.put(skill_text, tid, r, rec)
                if split == "train":
                    self._write_conversation(out, tid, dirs[tid], rec)
                records[(tid, r)] = rec

        results = [self._result(it, r, n_rep, records[(it["id"], r)])
                   for it in batch.items for r in range(n_rep)]
        self._write_summary(out, results, [records[(it["id"], r)]
                                           for it in batch.items for r in range(n_rep)])
        return results

    # ── helpers ──────────────────────────────────────────────────────────
    def _result(self, item: dict, r: int, n_rep: int, rec: dict | None) -> dict:
        rid = item["id"] if n_rep == 1 else f"{item['id']}@r{r}"
        task = self.task_index[item["id"]]
        base = {"id": rid, "task_id": item["id"], "task_type": task["category"],
                "task_description": task["task_text"]}
        if rec is None:
            return {**base, "hard": 0, "soft": 0.0, "fail_reason": "candidate rejected: test leakage",
                    "n_turns": 0, "env_error": False}
        if rec["env_error"]:
            reason = f"environment error: {str(rec['err_msg'])[:200]}"
        elif rec["cr"]:
            reason = ""
        else:
            missing = len(rec["gold_urls"]) - len(rec["found_urls"])
            reason = (f"F1={rec['f1']:.2f}; {missing} gold offer(s) missing, "
                      f"{len(rec['wrong_urls'])} wrong offer(s) submitted")
        return {**base, "hard": rec["cr"], "soft": rec["f1"], "precision": rec["precision"],
                "recall": rec["recall"], "fail_reason": reason, "n_turns": rec["n_steps"],
                "env_error": rec["env_error"], "input_tokens": rec["input_tokens"],
                "output_tokens": rec["output_tokens"]}

    def _write_conversation(self, out: Path, task_id: str, exp_dir: Path, rec: dict) -> None:
        conv = trajectory.build_conversation(self.steps_fn(exp_dir),
                                             self.task_index[task_id]["task_text"], rec)
        d = out / "predictions" / task_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "conversation.json").write_text(json.dumps(conv, ensure_ascii=False, indent=2))
        (d / "outcome.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))

    def _write_summary(self, out: Path, results: list[dict], records: list[dict]) -> None:
        n = len(results)
        summary = {
            "n": n,
            "hard": sum(r["hard"] for r in results) / n if n else 0.0,
            "soft": sum(r["soft"] for r in results) / n if n else 0.0,
            "env_errors": sum(1 for r in results if r.get("env_error")),
            "webmall": scoring.aggregate(records) if records else None,
            "agentlab_cost": sum(r.get("agentlab_cost", 0.0) for r in records),
            "cost": self.budget.spent(),
        }
        (out / "summary.json").write_text(json.dumps(summary, indent=2))
