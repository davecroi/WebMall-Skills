# skillopt_webmall — SkillOpt integration for WebMall

Not part of upstream WebMall or SkillOpt. Runs SkillOpt's validation-gated skill
optimisation (condition C3) on WebMall with `z-ai/glm-5.3-flash` (via OpenRouter) as optimizer and
target. Earlier runs used `deepseek/deepseek-v4.1-flash` (test data in `skillopt_results/archive/`). The archived run in `webmall_skills/results/skillopt/` used `gpt-6-luna`.
Design and known limitations: [`DESIGN.md`](DESIGN.md).

## Setup

    PY=Browsergym/.venv/bin/python
    git submodule update --init SkillOpt
    $PY -m pip install -e SkillOpt
    # .env at the repo root: shop URLs, OPENROUTER_API_KEY
    # shops running (docker_all/README.md)

Run every command from the repo root as `python -m webmall_skills…`. The entry points
change into the repo root themselves, and every path in the config (`skill_init`,
`split_dir`) is relative to the repo root, so an IDE run config from another folder
works too. Training refuses to start if `env.skill_init` or `env.split_dir` does not
exist (SkillOpt would otherwise start from a blank skill).

Prices: `env.price_input_per_m` / `env.price_output_per_m` in `configs/c3.yaml`
(USD per 1M tokens of z-ai/glm-5.3-flash) are used by the probe, training and the test
evaluation. The probe can override them with `--price-in` / `--price-out`; training
reads them only from the YAML (or `--cfg-options env.price_input_per_m=…`).

## Pipeline (each step ends with a go/no-go)

    $PY -m pytest webmall_skills -q                                             # no browser, no API

    # 1. step 0: base skill vs. no skill on val (go criteria: env errors < 10 %, base F1 < 0.85)
    $PY -m webmall_skills.skillopt_webmall.probe

    # 2. training (pilot first: one epoch, then the full run)
    $PY -m webmall_skills.skillopt_webmall.train --out_root skillopt_results/c3_pilot \
        --cfg-options train.num_epochs=1
    $PY -m webmall_skills.skillopt_webmall.train --out_root skillopt_results/c3_full

    # 3. run summaries (also works mid-run)
    $PY -m webmall_skills.skillopt_webmall.report skillopt_results/c3_full

    # 4. lineage export → webmall_skills/skills/skillopt/
    $PY -m webmall_skills.skillopt_webmall.export_lineage skillopt_results/c3_full \
        --ledger skillopt_results/c3_ledger.json

    # 5. held-out test (33 test tasks, one condition per call, then the summary)
    $PY -m webmall_skills.skillopt_webmall.test_eval best --credit 3.78   # USD left on the key
    $PY -m webmall_skills.skillopt_webmall.test_eval base
    $PY -m webmall_skills.skillopt_webmall.test_eval noskill
    $PY -m webmall_skills.skillopt_webmall.test_eval --summary-only

Warning: `test_eval --summary-only` and `probe --overview-only` rewrite the committed `summary.*` files under `webmall_skills/results/skillopt/` from the local caches (empty in a fresh clone). Restore them with `git checkout -- webmall_skills/results`.

`train` defaults to `--config configs/c3.yaml`; any SkillOpt CLI option works.
The test split can also be run through AgentLab directly: `webmall_skills_test` with
`skill = "skillopt"` in `run_webmall_study.py`.

## Where outputs land

| What | Where |
|---|---|
| Raw outputs: AgentLab runs, SkillOpt run dirs, rollout caches, cost ledgers | `skillopt_results/` (git-ignored; override with `SKILLOPT_RESULTS_DIR`) |
| Committed summaries: step 0, test evaluation, run results | `webmall_skills/results/skillopt/` (`probe/<split>/`, `test/`, …) |
| The C3 skill and its lineage (`SKILL.md`, `HISTORY.md`, `history/`, `run/`) | `webmall_skills/skills/skillopt/` |

Cost ledgers: `c3_ledger.json` (pilot and full run share the $25 ceiling),
`probe_ledger.json`, `test_ledger.json`.

## Modules

| Module | Purpose |
|---|---|
| `train.py` | entry point: registers `"webmall"` in SkillOpt's env registry, checks the config paths, runs SkillOpt's trainer |
| `configs/c3.yaml` | the C3 config (inherits `SkillOpt/configs/_base_/default.yaml`) |
| `adapter.py` | SkillOpt `EnvAdapter`: val repeats, rollout cache, leakage guard, budget guard; the test split is never rolled out |
| `dataloader.py` | SkillOpt dataloader for `webmall_skills/split/split_v2`; the test split loads as empty |
| `tasks.py` | task index from WebMall's `task_sets.json`, task types |
| `runner.py`, `agent_config.py` | AgentLab rollouts with the same agent (`agent_config.TARGET_AGENT` = `AGENT_GLM_53_FLASH_AX_M`) and skill injection as the test runs |
| `scoring.py` | per-task CR/P/R/F1 with WebMall's formulas |
| `trajectory.py` | condensed trajectories (`conversation.json`) for reflection: AX trees only for error, last-two and navigation steps, ≤ 8k chars each, ≤ 100k chars per trajectory |
| `leakage.py` | rejects candidates that contain test-task phrases, model tokens or answer slugs |
| `cache.py` | val rollout cache keyed by (skill text hash, task, repeat), shared by step 0 and training |
| `budget.py` | cost ledger with a hard ceiling |
| `probe.py` | step 0; `--overview-only` rebuilds the summary from the cache without rollouts |
| `report.py` | run summaries: `<run>/summary.md` (step timeline; best vs. base vs. no skill on val) and `steps/step_NNNN/summary.md` |
| `summary.py` | shared helpers for step 0, run and test summaries (efficiency metrics, tables) |
| `export_lineage.py` | run dir → `webmall_skills/skills/skillopt/` (deterministic) |
| `test_eval.py` | held-out test evaluation, one condition at a time, cached and budget-checked |
| `tests/` | unit tests (synthetic AgentLab folders, no browser, no API) |

## Adding a new condition

1. Copy `configs/c3.yaml` to `configs/<name>.yaml` and change what the condition changes
   (e.g. `use_slow_update`, `skill_init`, epochs). Paths stay relative to the repo root.
2. Choose a new `--out_root` and a new `env.budget_ledger`, so the run gets its own
   directory and its own ceiling (the default ledger `skillopt_results/c3_ledger.json`
   belongs to C3):

       $PY -m webmall_skills.skillopt_webmall.train --config webmall_skills/skillopt_webmall/configs/<name>.yaml \
           --out_root skillopt_results/<name> --cfg-options env.budget_ledger=skillopt_results/<name>_ledger.json

3. Report and export as above; export to a new skill folder with
   `export_lineage … --out webmall_skills/skills/<name>`, which makes it selectable as
   `skill = "<name>"` in `run_webmall_study.py`.

Val rollouts of byte-identical skill texts are reused from the cache across
conditions (e.g. the base-skill baseline from step 0).
