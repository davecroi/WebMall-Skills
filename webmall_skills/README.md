# webmall_skills — agent skills for WebMall

`webmall_skills` injects an agent skill (a `SKILL.md` document with learned strategies)
into the prompt of the AgentLab `GenericAgent` that runs the WebMall benchmark, so the
same agent can be compared with and without a skill. The skill is added to the user
message at every step under `## Skill Knowledge`, in the same format SkillOpt uses for
its ALFWorld environment (details: `docs/skill_injection.md`).

## Layout

```
pytest.ini                       # testpaths = webmall_skills, pythonpath = .
run_webmall_study.py             # agents + skill selector + split benchmarks
run_single_task.py               # agent + skill selector
webmall_skills/
  __init__.py
  README.md                      # this file
  paths.py                       # REPO_ROOT, PACKAGE_DIR, SKILLS_DIR, TASK_SETS_PATH, results_root(), resolve()
  injection.py                   # with_skill, SkillGenericAgentArgs, skill_path(), available_skills()
  contamination.py               # shared leakage blocklist (base-skill construction and SkillOpt guard)
  docs/
    skill_injection.md           # how and where the skill enters the prompt, and why
  tests/                         # core tests: injection, paths, contamination
  split/                         # shared train/val/test split
    README.md                    # how the split was drawn, v1 -> v2, file format, guarantees
    make_split.py                # rebuilds v1 (`--v1`) or the fixed v2
    benchmarks.py                # webmall_skills_{train,val,test} for run_webmall_study.py
    split_v2/                    # split_manifest.json, train|val|test/items.json
    tests/
  skills/                        # things you can inject (+ how they came to be)
    README.md                    # what a skill folder is, how to add one
    base/SKILL.md                # the hand-built base skill
    base/construction/           # provenance of the base skill (incl. evidence/)
    skillopt/                    # C3 skill: SKILL.md, README.md, SUMMARY.md, HISTORY.md, history/, run/
  skill_construction/            # base-skill construction mechanism (replaceable)
    README.md, build_sources.py, explore_shops.py, draft_skill.py, tests/
  skillopt_webmall/              # SkillOpt C3 integration
    README.md, DESIGN.md
    configs/c3.yaml
    train.py                     # training entry point
    tasks.py adapter.py dataloader.py runner.py agent_config.py scoring.py trajectory.py
    leakage.py cache.py budget.py summary.py report.py
    probe.py export_lineage.py test_eval.py
    tests/
  results/                       # measurements (not injectable)
    README.md                    # what each run is, headline numbers, what is not included
    skillopt/                    # probe/, c3_pilot/, c3_full/, test/, rollout_cache/, test_cache/,
                                 # ledgers/, logs/
```

## How the parts depend on each other

```
paths  <-  injection, contamination, split  <-  skill_construction (base skill)
                                            <-  skillopt_webmall (C3)
run_webmall_study.py / run_single_task.py  ->  injection, split.benchmarks
```

Documentation per part: [`docs/skill_injection.md`](docs/skill_injection.md),
[`skills/README.md`](skills/README.md), [`skill_construction/README.md`](skill_construction/README.md),
[`split/README.md`](split/README.md), [`skillopt_webmall/README.md`](skillopt_webmall/README.md)
(design: [`DESIGN.md`](skillopt_webmall/DESIGN.md)), [`results/README.md`](results/README.md).

All config and package paths are derived from `paths.py` and resolve against the repository
root from any working directory. CLI arguments you pass (`RUN_DIR`, `--out`, `--ledger`,
`--out_root`) are relative to where you run the command (`train`, `probe` and `test_eval`
chdir to the repo root first). Raw experiment outputs go to the
git-ignored folder `skillopt_results/` (override with `SKILLOPT_RESULTS_DIR`).

## Setup

```bash
git submodule update --init --recursive    # Browsergym, AgentLab, SkillOpt
python3.12 -m venv Browsergym/.venv && source Browsergym/.venv/bin/activate
(cd Browsergym && make install)            # pip-installs into the active venv
Browsergym/.venv/bin/pip install pytest
Browsergym/.venv/bin/pip install -e AgentLab
Browsergym/.venv/bin/pip install -e SkillOpt
cp .env.example .env                       # then fill in OPENROUTER_API_KEY
```

## Run with a skill

In `run_webmall_study.py` (or `run_single_task.py`), next to the agent selection:

```python
skill = None          # no-skill baseline
# skill = "base"       # webmall_skills/skills/base/SKILL.md
# skill = "skillopt"   # webmall_skills/skills/skillopt/SKILL.md
# skill = "path/to/any.md"
```

A name selects `webmall_skills/skills/<name>/SKILL.md`; an unknown name raises
`FileNotFoundError` listing the available skills before any browser starts. Skills only
work with `agentlab.agents.generic_agent.GenericAgentArgs` agents (the `AGENT_*_AX_M`
agents); the WebMall presets such as `AGENT_4o` raise `TypeError`. To add a skill, see
`skills/README.md`.

## Task split

The shared train/val/test split of the 91 tasks lives in `webmall_skills/split/` and is
selectable in `run_webmall_study.py` as `webmall_skills_{train,val,test}`. How it was
drawn, its v1 to v2 extension and its guarantees: `webmall_skills/split/README.md`.

## Run the tests

```bash
Browsergym/.venv/bin/python -m pytest
```

## SkillOpt (C3)

`webmall_skills/skillopt_webmall/` evolves the base skill with SkillOpt's validation-gated
fast loop (condition C3, `deepseek/deepseek-v4.1-flash` (via OpenRouter) as optimizer and target; the archived run in
`results/skillopt/` used `gpt-6-luna`):

1. step 0 `python -m webmall_skills.skillopt_webmall.probe`: base skill vs. no skill on val
2. training `python -m webmall_skills.skillopt_webmall.train --out_root skillopt_results/c3_full`
3. summaries `python -m webmall_skills.skillopt_webmall.report skillopt_results/c3_full` and lineage export to `webmall_skills/skills/skillopt/`
4. held-out test `python -m webmall_skills.skillopt_webmall.test_eval {best,base,noskill}`
5. raw outputs in `skillopt_results/`, committed summaries in `webmall_skills/results/skillopt/`

Commands, outputs and how to add a condition: [`skillopt_webmall/README.md`](skillopt_webmall/README.md).

## How to extend

- **New skill:** add `skills/<name>/SKILL.md`; it is immediately selectable as `skill = "<name>"` (see `skills/README.md`).
- **New SkillOpt condition:** add a config next to `skillopt_webmall/configs/c3.yaml` and run it through `skillopt_webmall/train.py`; see `skillopt_webmall/README.md`.
- **Reworking the base-skill construction:** `skill_construction/` is replaceable. Only `skills/base/SKILL.md` is consumed elsewhere, and the shared leakage blocklist lives in `contamination.py`, so changing or deleting `skill_construction/` does not break C3.
- **Adding a split:** add `split/split_v3/` with a manifest whose `extends` records the sha256 of the previous manifest. Generate it by calling `extend_split` from new code (`make_split.py` only writes v1 or v2). Add `webmall_skills_v3_*` entries to `SPLIT_BENCHMARKS` in `split/benchmarks.py` with `split_dir` pointing at the new folder, and point `env.split_dir` in a new SkillOpt config at it. `extend_split` hard-codes `extends.split = "split"` and the v2 `reason`, so a v3 manifest must set its own `extends.split` and `reason`. Never re-draw the test split.
