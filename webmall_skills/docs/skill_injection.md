# Skill injection for WebMall runs (`webmall_skills/injection.py`)

Thesis code, not part of upstream WebMall/AgentLab. It lets `run_webmall_study.py`
run the same agent under different skill conditions (no skill, hand-written skill,
self-improved skill, recursively self-improved skill) by selecting a `SKILL.md` file.

## Usage

In `run_webmall_study.py`, next to the agent and benchmark selection:

```python
agent_args = [AGENT_41_AX_M]

skill = None          # no-skill baseline
# skill = "base"       # hand-built base skill
# skill = "skillopt"   # SkillOpt C3 skill (best of the C3 run)

agent_args = [with_skill(a, skill_path(skill)) for a in agent_args]
```

- `skill` is `None`, a skill name (`"base"`, `"skillopt"`, … resolves to
  `webmall_skills/skills/<name>/SKILL.md`) or a path to any `.md` file (relative
  paths resolve against the repository root). An unknown name raises
  `FileNotFoundError` listing the available skills, before any browser starts.
- `skill = None` leaves the agent untouched (`with_skill` returns the
  original `GenericAgentArgs`), so the baseline is the unmodified WebMall agent.
- Works with `agentlab.agents.generic_agent.GenericAgentArgs` (the `AGENT_*_AX_M` agents
  in `run_webmall_study.py`, including the OpenRouter agents `AGENT_OR_41_AX_M`,
  `AGENT_OR_CLAUDE_AX_M`); the WebMall presets `AGENT_4o`, … raise `TypeError`.
- `with_skill(agent, skill_text=..., skill_name=...)` injects a skill given as text
  instead of a file (used by the SkillOpt adapter in `webmall_skills/skillopt_webmall/`, where
  candidate skills only exist in memory). The text is stored in `exp_args.pkl` the
  same way, and `skill_name` becomes the `-skill_<name>` suffix.

## Base skill

`webmall_skills/skills/base/SKILL.md` is the frozen base skill (condition "base skill" and seed
for self-improvement). Its full provenance is in `webmall_skills/skills/base/construction/`;
the method is described in `webmall_skills/skill_construction/README.md`. Do not edit it
after benchmark runs have started; changes belong to the self-improvement phase.

## What `injection.py` does

- `SkillGenericAgentArgs` extends AgentLab's `GenericAgentArgs` with
  `skill_path`, `skill_text` and `skill_name`.
- **Reproducibility:** the file is read once when the args are created and the
  text is stored in `skill_text`. AgentLab pickles the agent args into each
  experiment's `exp_args.pkl`, so every result folder records the exact skill
  text it ran with, even if the file is edited later.
- **Naming:** `agent_name` gets the suffix `-skill_<name>`, so result folders
  show the condition. `<name>` is the parent folder for `SKILL.md` files,
  otherwise the file stem.
- **Injection:** `make_agent()` copies the flags (shared flag objects such as
  `FLAGS_AX_M` are not modified) and appends the skill block to
  `extra_instructions`. Everything else about the agent is unchanged.
- No vendored code is modified.

## Where the skill ends up in the request

Request flow per browser step (AgentLab submodule at commit `3c70b91`):

1. `GenericAgent.get_action()` builds two messages
   (`AgentLab/src/agentlab/agents/generic_agent/generic_agent.py:114`):
   - **System message:** `dp.SystemPrompt()`, a fixed 3-line text
     (`AgentLab/src/agentlab/agents/dynamic_prompting.py:566`). Not changed.
   - **User message:** `MainPrompt._prompt`
     (`AgentLab/src/agentlab/agents/generic_agent/generic_agent_prompt.py:104`),
     in this order: instructions (goal + `## Extra instructions`), observation
     (AX tree), history, action space, hints, think/memory sections, examples.
2. `extra_instructions` is rendered by `GoalInstructions`
   (`dynamic_prompting.py:479`, heading at line 504), directly after the goal.
3. The messages are sent via the model class in
   `AgentLab/src/agentlab/llm/chat_api.py` (`client.chat.completions.create`).

So the skill is in the **user message, at every step, directly after the task
goal and before the page observation**. Rendered example (with `FLAGS_AX_M`,
whose memory instruction comes first):

```
## Extra instructions:

Use your memory to note down important information like the URLs of potential solutions and corresponding pricing information.

## Skill Knowledge
Below is a skill document with learned strategies. Use these guidelines to inform your decisions:

<full SKILL.md content>
```

The skill name is deliberately **not** in the prompt, so condition labels such as
`recursive_self_improved` cannot leak to the model.

## Why this placement: SkillOpt reference

SkillOpt (vendored at `SkillOpt/`, upstream `microsoft/SkillOpt` commit
`79124b37e9a6371e13b753f8bcd7adb1e493ade1`) places the skill differently per
environment type:

| SkillOpt environment | Type | Skill placement | Reference |
|---|---|---|---|
| `alfworld` | multi-step agent (observe → act loop) | **user message, every step, before the observation**; fixed one-line system prompt | `skillopt/envs/alfworld/rollout.py:48` (`_build_skill_prompt`), `:220` (`prompt = skill_prompt + "\n" + prompt`), `:231` (system prompt) |
| `searchqa` | QA | system prompt, `## Skill` section | `skillopt/envs/searchqa/rollout.py:57` |
| `docvqa` | QA | system prompt | `skillopt/envs/docvqa/rollout.py:14` |
| `livemathematicianbench` | QA | system prompt | `skillopt/envs/livemathematicianbench/rollout.py:14` |
| `officeqa` | QA / tool use | system prompt | `skillopt/envs/officeqa/rollout.py:74` |
| `spreadsheetbench` | code-gen / ReAct agent | system prompt | `skillopt/envs/spreadsheetbench/codegen_agent.py:139`, `react_agent.py:108` |
| `_template` | guidance for new envs | "use `skill_content` as the system message" | `skillopt/envs/_template/env_template.py:106` |

WebMall's AgentLab agent has the same structure as ALFWorld: a fixed short system
prompt and a per-step user message containing observation, history and action
space. We therefore follow the **ALFWorld** convention: user message at every
step, with ALFWorld's exact wrapper text (`## Skill Knowledge` + lead-in sentence,
copied from `rollout.py:48–57`). This keeps the prompt format the skill is
**trained** in (SkillOpt rollouts) identical to the format it is **evaluated** in
(WebMall runs).

Note: the docstring of `_build_skill_prompt` says "inject into the agent's system
prompt", but the code at `rollout.py:220` prepends it to the user prompt. Cite
the code, not the docstring.

Deviation from ALFWorld: ALFWorld puts the skill at the very top of the user
message; here it follows the task goal inside `## Extra instructions` (still
before the observation). This avoids modifying AgentLab's `MainPrompt`.

## Context: how agent harnesses load skills

For comparison when motivating the design (not used by this code):

- **Claude Code:** progressive disclosure. Only each skill's name and description
  (from the `SKILL.md` frontmatter) are in context at the start; the full
  `SKILL.md` is loaded into the conversation (user side, not the system prompt)
  when the skill is invoked. Referenced files are read on demand.
- **Pi coding agent:** lists available skills (name, description, path) in the
  system prompt; the model loads a skill with its `read` tool, or the user forces
  one with `/skill:name`. *(From memory; verify against Pi's docs before citing.)*

Progressive disclosure doesn't fit WebMall: the AgentLab agent has no file-reading
tool, and a single skill is relevant to every task. Always injecting the full
text also makes the comparison cleaner: differences between conditions come from
the skill's content, not from whether the agent chose to load it.

## Caveats and future work

- **Frontmatter is included.** The full file goes into the prompt, as in ALFWorld.
  If SkillOpt's `best_skill.md` has no YAML frontmatter, hand-written skills
  should not have it either, so all conditions share the same format.
- **Offline improvement only.** Each condition is a fixed file for the whole run.
  Updating the skill *during* a benchmark run (between tasks) would need
  sequential execution and an update step after each task; parallel Ray workers
  would otherwise see different skill versions.
- **Token cost.** The skill is repeated in every step's prompt and counts towards
  `max_prompt_tokens`; long skills leave less room for the AX tree and history.
- **Prompt caching.** System prompt + goal + skill form a prefix that is identical
  across steps of one task (the observation comes after it), so automatic prefix
  caching can apply within a task. Across tasks the goal changes, so a
  system-prompt skill would give a longer shared prefix.
- **Moving it to the very top** of the user message (exact ALFWorld position)
  would require a small `MainPrompt` subclass in `injection.py`.
