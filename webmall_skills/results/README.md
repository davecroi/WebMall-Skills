# Results already obtained

Curated snapshot of the SkillOpt step 0 probes, the C3 pilot and full run, and the held-out test
evaluation. Everything lives under `skillopt/`. Numbers below are copied from the quoted file;
F1 and CR are means over per-task runs (Luna agent, 50 steps).

| Run | What it is | Key file | Headline numbers |
|---|---|---|---|
| `probe/split` | Step 0 on split v1 (pilot), 11 val tasks | `skillopt/probe/split/summary.md` | base skill (x2) F1 0.755 / CR 0.682; no skill (x1) F1 0.775 / CR 0.636; decision GO; $0.88 for 33 rollouts |
| `probe/split_v2` | Step 0 on split v2, 21 val tasks | `skillopt/probe/split_v2/summary.md` | base skill F1 0.705 / CR 0.667; no skill F1 0.707 / CR 0.571; decision GO; $0.62 for 20 new rollouts |
| `c3_pilot` | C3, 1 epoch on split v1 (1 step) | `skillopt/c3_pilot/summary.md` | step 1 candidate val F1 0.709 (delta -0.045), rejected by the gate; best = base (v0000); $1.02 |
| `c3_full` | C3, 4 epochs, 8 steps on split v2 (21 val tasks) | `skillopt/c3_full/summary.md` | accepted steps 2, 5, 7; rejected 1, 3, 4, 6, 8; best = v0007. Val F1 best 0.865, base skill 0.705, no skill 0.707; $8.59 training cost |
| `test` | Held-out evaluation, 33 test tasks, 1 run per skill | `skillopt/test/summary.md` | F1 best (C3 v0007) 0.824, base skill 0.840, no skill 0.820 |
| ledgers | Token and USD cost per phase | `skillopt/ledgers/*.json` | total_usd: probes 1.4955 (53 rollouts), C3 9.8569 (316 rollouts; optimizer 0.4293), test 2.4638 (99 rollouts) |

The best skill was selected on the val tasks, so its val score is optimistic; the test row is the
unbiased comparison (best does not beat the base skill there).

## Layout

- `skillopt/c3_pilot/`, `skillopt/c3_full/`: every file of the SkillOpt run directory (config,
  history, report, summaries, skills, candidate skills, step records, `outcome.json` per rollout)
  except AgentLab runs and per-rollout conversation files.
- `skillopt/rollout_cache/`, `skillopt/test_cache/`: per-task rollout records (F1, CR, tokens, ...).
- `skillopt/ledgers/`: `probe_ledger.json`, `c3_ledger.json`, `test_ledger.json`.
- `skillopt/logs/`: console logs, gzipped.
- `skillopt/probe/<split>/`, `skillopt/test/`: committed summaries (`summary.md`, `summary.json`).

## What is not here and why

- AgentLab step pickles (about 1.5 GB) and `conversation.json` files (about 15 MB): too large.
- Raw AgentLab runs of the probes and of the test evaluation.
- The aborted `c3_pilot_failed_max_tokens` run (it hit the `max_tokens` bug fixed by
  `openai_compat.py`); the successful `c3_pilot` replaces it.

All of these are kept in the local thesis repository.

## Snapshot, not regenerable

Warning: `test_eval --summary-only` and `probe --overview-only` rewrite the committed `summary.*` files under `webmall_skills/results/skillopt/` from the local caches (empty in a fresh clone). Restore them with `git checkout -- webmall_skills/results`.

`report.py`, `probe --overview-only` and `test_eval --summary-only` read AgentLab run directories
(`summary_info.json`, step pickles) for timing and outcomes. Those are not committed, so these
summaries cannot be regenerated from this folder. Absolute paths were scrubbed: `exp_dir` in the
caches is relative to the original results root (`skillopt_results/`), and path values in the run
files (`out_root`, `exp_dir` in `outcome.json`) are relative to the thesis `WebMall/` directory
(so they start with `skillopt_results/`). Summaries are verbatim and still mention the old
benchmark name `webmall_thesis_test_v1.0`; it is now the split benchmarks `webmall_skills_*`.

## Where new runs go

New runs write to `skillopt_results/` (git-ignored). The commands that write committed summaries
into this folder are `probe` (to `skillopt/probe/<split dir name>/`) and `test_eval` (to
`skillopt/test/`).
