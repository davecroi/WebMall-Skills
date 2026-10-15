# webmall_skills — agent skills for WebMall

`webmall_skills` injects an agent skill (a `SKILL.md` document with learned strategies)
into the prompt of the AgentLab `GenericAgent` that runs the WebMall benchmark, so the
same agent can be compared with and without a skill. The skill is added to the user
message at every step under `## Skill Knowledge`, in the same format SkillOpt uses for
its ALFWorld environment (details: `docs/skill_injection.md`).

## Layout

```
pytest.ini                       # testpaths = webmall_skills, pythonpath = .
run_webmall_study.py             # agents + skill selector
run_single_task.py               # agent + skill selector
webmall_skills/
  __init__.py
  README.md                      # this file
  paths.py                       # REPO_ROOT, PACKAGE_DIR, SKILLS_DIR, TASK_SETS_PATH, results_root(), resolve()
  injection.py                   # with_skill, SkillGenericAgentArgs, skill_path(), available_skills()
  docs/
    skill_injection.md           # how and where the skill enters the prompt, and why
  tests/                         # core tests: injection, paths
  skills/
    README.md                    # what a skill folder is, how to add one
    base/SKILL.md                # the hand-built base skill
```

All paths are derived from `paths.py` and anchored at the repository root, so scripts
and tests behave the same from any working directory. Raw experiment outputs go to the
git-ignored folder `skillopt_results/` (override with `SKILLOPT_RESULTS_DIR`).

## Setup

```bash
git submodule update --init --recursive    # Browsergym, AgentLab, SkillOpt
cd Browsergym && make install && cd ..     # creates Browsergym/.venv
Browsergym/.venv/bin/pip install -e AgentLab
Browsergym/.venv/bin/pip install -e SkillOpt
cp .env.example .env                       # then fill in OPENAI_API_KEY / OPENROUTER_API_KEY
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
fast loop (condition C3, `gpt-6-luna` as optimizer and target):

1. step 0 `python -m webmall_skills.skillopt_webmall.probe`: base skill vs. no skill on val
2. training `python -m webmall_skills.skillopt_webmall.train --out_root skillopt_results/c3_full`
3. summaries `python -m webmall_skills.skillopt_webmall.report` and lineage export to `skills/skillopt/`
4. held-out test `python -m webmall_skills.skillopt_webmall.test_eval {best,base,noskill}`
5. raw outputs in `skillopt_results/`, committed summaries in `webmall_skills/results/skillopt/`

Commands, outputs and how to add a condition: [`skillopt_webmall/README.md`](skillopt_webmall/README.md).
