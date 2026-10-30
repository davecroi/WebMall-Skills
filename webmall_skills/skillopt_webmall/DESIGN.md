# SkillOpt on WebMall — C3 design

Condensed from the thesis design spec of 2026-10-07 (with its 2026-10-13 `split_v2`
amendment). Paths refer to this repository.

## Goal: condition C3

The thesis question is whether an agent can improve its own skill document by
self-improvement and whether that helps on held-out tasks. **C3** (single-level
self-improving skill) answers the first half: a skill evolved from the frozen base skill
(`webmall_skills/skills/base/SKILL.md`) by SkillOpt's validation-gated fast loop, with a
complete, readable history of every candidate edit and of which versions became the new
best skill. C3 is compared with no skill and the base skill on the held-out test split.

C4 (MetaSkill-Evolve, fast + slow loop) is out of scope. The adapter, split and rollout
cache are built so C4 can reuse them.

## Decisions

| Topic | Decision |
|---|---|
| Split | Stratified split of the 91 WebMall tasks by category, seed 42 (matches SkillOpt `train.seed`), drawn once and committed before any experiment. v1: 1/1/3 per category (11/11/33). Runs after the pilot use `split_v2` (26/21/33), see below. |
| Optimizer model | `z-ai/glm-5.3-flash` via OpenRouter; earlier runs used `deepseek/deepseek-v4.1-flash` and `gpt-6-luna` (self-improvement: the agent improves its own skill; matches SkillOpt's default optimizer = target). |
| Target model | `z-ai/glm-5.3-flash` via OpenRouter, AX tree + memory (`AGENT_GLM_53_FLASH_AX_M`, selected in `agent_config.py`); earlier runs used `deepseek/deepseek-v4.1-flash` and `gpt-6-luna`. |
| Base skill author | `gpt-6.1-sol` (a fixed starting artefact, disclosed). |
| SkillOpt mode | Fast loop only: `use_slow_update: false`, `use_meta_skill: false`. |
| Gate metric | `mixed`, weight 0.04: 0.96 × mean CR + 0.04 × mean per-task F1 over val (`split_v2`: 21 tasks × 1 repeat). Task completion decides; F1 only breaks ties, since one more completed task (0.96/21 = 0.046) outweighs any F1 difference (≤ 0.04). |
| Training budget | 2 epochs, batch 13 (2 steps per epoch, 4 gated steps), hard ceiling **$25** shared by pilot and full run. |
| Integration | In-process adapter in `webmall_skills/skillopt_webmall/`; no SkillOpt or WebMall file is edited. |
| History | Curated lineage export to `webmall_skills/skills/skillopt/`, rejected candidates included. |

## Deviations from SkillOpt defaults

- **Slow update and meta skill off.** C3 is pure validation-gated editing; all epoch-level
  and meta mechanisms belong to C4. SkillOpt's "meta skill" (passive optimizer memory) is
  not MetaSkill-Evolve's meta-skill.
- **Backend `openai_compatible`** for both roles (SkillOpt's `openai_chat` is Azure-only),
  pointed at OpenRouter (`OPENROUTER_API_KEY`) by `train.configure_env()`. Temperature is
  not sent to the optimizer (provider default); the target agent uses 1, like Luna.
- **Val repeats and batch size** come from the split (below); all other values stay at
  SkillOpt's defaults and are recorded in each run's `config.json`.

## Split (`webmall_skills/split/`)

- Tasks are grouped by task set (11 categories), sorted within each group and shuffled
  with `random.Random(42)`; positions 0 → train, 1 → val, 2–4 → test, rest → unused.
- SkillOpt's manifest layout: `split_manifest.json` (seed, source path + sha256, counts,
  per-category assignment, unused IDs) and `{train,val,test}/items.json` with IDs only.
- The test split is shared by every condition and backbone. Training code never loads
  it: the dataloader returns `test/` as empty, the adapter refuses to roll it out, and
  the config sets `test_env_num: 0`, `eval_test: false`.

### Amendment: `split_v2` (larger train and val, val × 1)

- **Why:** the one-epoch pilot (v1) had train F1 0.94 (one failure minibatch to reflect
  on), and its step-1 rejection (val F1 0.709 vs. 0.755 over 22 rollouts) was about one
  task flipping, within the gate's noise.
- **How:** `make_split.py` (default action, `extend_split`) keeps v1's train/val/test and, per category, moves
  the next unused tasks in the stored seed-42 order to val (+1), then train (+2).
  Nothing is re-drawn; **test is byte-identical to v1**. The manifest records the v1
  manifest's sha256, the extra counts, the reason and the added IDs.
- **Counts:** train 26, val 21, test 33, unused 11 (categories with too few unused tasks
  get less).
- **Config:** `split_dir: webmall_skills/split/split_v2`, `val_repeats: 1` (more tasks
  instead of repeats: repeats only measure agent noise on the same tasks), `batch_size: 13`.
- Step 0 was re-run on the v2 val set; base-skill rollouts of the 11 v1 val tasks were
  reused from the cache.

## Adapter (`adapter.py`, `runner.py`, `scoring.py`, `trajectory.py`)

**Rollout** of a batch with a candidate skill text:

1. The agent is `with_skill(TARGET_AGENT, skill_text=…, skill_name=…)`, the same
   injection used for test runs (skill under `## Skill Knowledge`).
2. The batch's task IDs run as one AgentLab study (`runner.run_tasks`, 50 steps,
   `n_relaunch=1`), one study per repeat, under `<out_dir>/agentlab/r<k>/`.
3. Per task (`scoring.read_outcome`): `hard` = CR (exact set match), `soft` = per-task F1
   with the formulas of `analyze_agentlab_results/summarize_study.calculation_results`;
   add-to-cart and checkout tasks use their checklist score, as WebMall does. Extra
   fields: steps, tokens, `env_error`. The gate uses mean CR, then the mean of per-task F1; WebMall's
   reported F1 is computed from averaged P and R, so the two can differ slightly. Both
   are reported.
4. Train rollouts write `conversation.json` for SkillOpt's reflection: every step's URL,
   think, memory, action and action error; AX trees only for action-error steps, the
   last two acting steps and navigation steps (≤ 8k chars each, ≤ 100k chars per
   trajectory, filled in that priority); the last message holds submission, gold
   solution and the per-task scores. The agent itself only sees the current page's tree
   plus condensed history, and full trees (~136–157k tokens per task) would not fit
   SkillOpt's minibatch reflection.

**Failure handling:** a browser or environment crash is relaunched once; if it fails
again it scores 0 and is flagged `env_error`.

## Rollout cache (`cache.py`)

Val results are keyed by `(sha256(skill text), task id, repeat index)` and stored outside
the run dir (`skillopt_results/rollout_cache`). Only val rollouts are cached (step 0
included); train rollouts are always fresh so every epoch samples new trajectories.
The base-skill val baseline is computed once in step 0 and reused. Hits only on
byte-identical skill text. Env-error records are not cached, so they are retried.

## Budget (`budget.py`)

Cumulative cost = (target tokens from AgentLab's `summary_info.json` + optimizer tokens
from SkillOpt's token tracker) × the configured Luna prices. The ledger file is shared by
the pilot and the full run, so the $25 ceiling covers both; step 0 and the test
evaluation have their own ledgers. Checked before every rollout batch (spent + missing
rollouts × observed mean cost per rollout; a train step also reserves the validation
that follows it). If the ceiling would be exceeded, training stops cleanly and
`best_skill.md` holds the best skill so far.

## Gate and test-leakage rule (`leakage.py`)

SkillOpt accepts a candidate only if its val `soft` score beats the current best.

The optimizer sees train trajectories including their gold URLs, and products recur
across tasks, so a train answer written into the skill could be a test answer. Before a
candidate's val rollouts the adapter checks it against a blocklist built from the **test
split only** (task texts, 3-word phrases, model tokens, answer slugs; shared with the
base-skill construction in `webmall_skills/contamination.py`). Any hit → candidate
rejected without val rollouts (scored 0), labelled `rejected (test_leakage)`. Train
vocabulary is not blocked (overfitting is what the gate measures). Val tasks never reach
the optimizer, since reflection uses train rollouts only.

## Lineage export (`export_lineage.py` → `webmall_skills/skills/skillopt/`)

`SKILL.md` (= the run's `best_skill.md`), `HISTORY.md`, `history/` (`v0000_base.md`,
`vNNNN.md`, `vNNNN.diff` against the parent, `vNNNN.edits.json`), `run/` (`config.json`,
`history.json`, `split_manifest.json`, `cost.json`), `README.md`, and `SUMMARY.md` when
the report was run. `HISTORY.md` columns: version, epoch, parent, edit summaries, val F1
before → after, val CR, decision (`seed` / `accepted` / `rejected (gate)` /
`rejected (test_leakage)` / `skipped (…)`), ★ for every new best (the last ★ is
`SKILL.md`). After a rejection the next candidate branches from the last accepted
version. The export is deterministic: same run dir → byte-identical output.

## Execution order

0. **Step 0:** Luna + base skill on val (cached as the gate baseline) and Luna without
   skill × 1. Go criteria: env errors < 10 % of tasks, base-skill val F1 < 0.85
   (headroom).
1. **Pilot:** one epoch; compare actual with estimated cost, inspect one
   `conversation.json` and the first candidate edit.
2. **Full C3 run** (2 epochs) → report → export → review `HISTORY.md` and `SKILL.md`.
3. **Held-out test** of best / base / no skill on the 33 test tasks, one run each.

## Thesis disclosures

- C3 deviates from SkillOpt defaults (slow update and meta skill off).
- The base skill was written by `gpt-6.1-sol`; all self-improvement uses `gpt-6-luna`.
- The gate ranks by mean CR, then mean per-task F1; reported F1 follows WebMall's aggregate formula.
- Luna supports only temperature 1, so val scores are noisy and the gate stays coarse.
- Train and val were enlarged after the pilot; test was never changed.
- Reflection input is condensed (selective AX trees), not the full observation stream.

## Known limitations

- **The cache key has no model id.** Val rollouts cached by one target model are reused
  for any other. The archived gpt-6-luna caches must not be copied into the results root
  of a DeepSeek or GLM run; use a fresh `SKILLOPT_RESULTS_DIR` per target model, or move the old
  caches into `skillopt_results/archive/` first.
- **`export_lineage` deletes `--out` without checking it.** It `rmtree`s the output
  folder before writing; point `--out` only at an export folder.
- **The `task_type` regex is narrower than WebMall's** (`^(.*?_Task)\d+$` vs.
  `summarize_study`'s `^(.*?_Task)\d+(?:_\d+){0,2}$`). No current task id is affected.
- **A leaky candidate served from SkillOpt's selection cache** is labelled
  `rejected (gate)` instead of `rejected (test_leakage)` (rare; it is still rejected).
- **Env-error train rollouts reach reflection** as agent failures (`hard = 0`).
