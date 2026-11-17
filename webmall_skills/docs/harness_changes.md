# Changes to the evaluation harness (AgentLab, BrowserGym/WebMall) and why

This log lists every change made to the third-party code that runs and scores the agent,
plus the experiment-setup decisions that affect results. It is meant as the source for the
"Experimental setup" and "Threats to validity" parts of the thesis: what changed, why, what
evidence motivated it, and which runs it affects.

Last updated: 2026-11-17.

## Code bases and baselines

| Component | Role | Upstream | Our version |
|---|---|---|---|
| AgentLab | agent (GenericAgent: prompt, answer parsing, retries), LLM client, study runner | ServiceNow/AgentLab, merged up to 2025-10-15 (`4b9961d`) | fork `davecroi/AgentLab`, branch `revert-reasoning-retry` |
| BrowserGym + WebMall task | browser environment, WebMall tasks and evaluators | `wbsg-uni-mannheim/BrowserGym` at `1aaef63` (2025-07-29) | fork `davecroi/BrowserGym`, branch `webmall-evaluator-wait-for-navigation` |
| This repo | agent configurations (`run_webmall_study.py`), skill injection, SkillOpt integration | — | `main` |

Both submodules are pinned by commit in this repo, so every result directory can be tied to an
exact harness version through the repo commit it was run from (and `package_versions.txt` in
each experiment folder).

## Overview

| ID | Date | Component | Commit | Kind | Affects scores? | Status |
|---|---|---|---|---|---|---|
| H1 | 2026-10-01 | AgentLab | `42e3f67` | cost tracking | no | active |
| H2 | 2026-10-20 | AgentLab | `6d88946` | retry from original prompt (DeepSeek) | yes | reverted 2026-11-05, partly restored by H11 |
| H3 | 2026-10-22 | AgentLab | `3172f15` | DeepSeek parsing, reasoning as `<think>`, think cap | yes | reverted 2026-11-05 |
| H4 | 2026-10-22 | AgentLab | `b0dc191` | OpenRouter provider routing, reported cost | indirectly (provider) | active |
| H5 | 2026-10-26 | AgentLab | `fd9b03c` | result analysis crash with pandas 3 | no | active |
| H6 | 2026-11-05 | AgentLab | `25d8183`, `33c6adc` | revert of H2 and H3 | yes | active |
| H7 | 2026-11-05 | AgentLab | `5d3cc37` | OpenRouter `reasoning` option | only if used (not used for GLM) | active |
| H8 | 2026-11-05 | AgentLab | `5472ea4` | `content=None` → `""` | yes (crash fix) | active |
| H9 | 2026-11-05 | BrowserGym/WebMall | `53a84e8` | evaluator waits for pending requests/navigation | yes (evaluation fix) | active |
| H10 | 2026-11-05 | this repo | `6d05853` | 5 parallel jobs (Ray) | indirectly (load, timeouts) | active |
| **H11** | 2026-11-17 | AgentLab + this repo | `4350801` | **answer repair + retry from original prompt** | **yes** | **new, to be frozen before the final runs** |

H1–H9 are summarized from their commit messages and the analyses at the time. H11 is documented
in full, including the evidence, since it is the change the final experiments depend on.

---

## H11 — Answer-format robustness: action repair and retry from the original prompt (2026-11-17)

### Problem

GenericAgent asks the model to answer with `<think>…</think>`, `<memory>…</memory>` and exactly
one `<action>…</action>`. If the answer cannot be parsed, AgentLab appends the answer and an
error message ("Missing the key <action> in the answer.") to the conversation and asks again, up
to 4 times (`max_retry = 4`). After the 4th failure the agent returns no action and **the episode
ends** (counted as "truncated"), whatever the agent had achieved so far.

On the 33-task test split (z-ai/glm-5.3-flash, one run per task) this ended:

| Condition | Episodes ended by the answer format | F1 (all 33 tasks) |
|---|---|---|
| no skill | 0 / 33 | 0.755 |
| lite skill | 8 / 33 | 0.568 |
| SkillOpt-optimized lite skill | 17 / 33 | 0.394 |

So the failure is not evenly distributed: it grows with the injected skill text and dominates
the comparison between conditions. On the 14 tasks where no condition aborted, the order is
reversed (F1 0.571 / 0.605 / 0.643). Details:
`task_results/2026-11-06_findings_noskill-vs-lite-vs-skillopt-glm-lite.md`.

### Analysis of the failed answers

All 728 failed answers logged in the runs made with the current AgentLab version (four test
runs and the SkillOpt `glm_lite` run, 244 episodes) were classified
(`task_results/2026-11-17_parser_replay/`):

| Kind of failed answer | Count | Contains a usable action? |
|---|---|---|
| the model's native tool-call syntax, e.g. `…<tool_call>goto('http://localhost:8081/?s=DDR5&post_type=product')`, often unclosed or with junk such as `</arg_value>` | 255 | yes, in 246 cases |
| several `<action>` tags | 116 | when all tags hold the same action (55 cases) |
| one `<action>` tag with an invalid action | 3 | no |
| prose only, no action | 257 | no |
| empty answer | 97 | no |

GLM models have a native tool-calling format (`<tool_call>` in their chat template). The model
sometimes falls back to it, more often with a skill in the prompt, and writes its action in that
syntax instead of the requested `<action>` tag. AgentLab's parser then rejects an answer whose
action is unambiguous.

The retries do not recover from this; once an answer has failed, the next one is far more likely
to fail than a first answer:

| Run | First answers that fail | Retry fails, given the previous attempt failed (attempt 2 / 3 / 4) |
|---|---|---|
| no skill (test) | 4.4–5.7 % | 5–8 % / 0 % / – |
| lite (test) | 12.6 % | 27 % / 54 % / 62 % |
| optimized (test) | 12.4 % | 41 % / 95 % / 94 % |
| SkillOpt glm_lite (train + val) | 11.0 % | 29 % / 63 % / 78 % |

If retries were independent samples, each would fail with about the first-answer rate
(≈ 12 %), and all four would fail in about 0.02 % of steps. Instead, the model sees its own
malformed answer in the conversation and repeats the format. The same effect was measured
earlier with deepseek-v4.1-flash (19 % of first answers malformed vs. 73–82 % of the 3rd and 4th
retries; H2).

### What was changed

Two opt-in options, both off by default so AgentLab's behaviour for other users and benchmarks is
unchanged, and both switched on for our agent configuration `FLAGS_AX_M` (used by all WebMall
agents, the skill-injected agents and SkillOpt's rollouts).

**1. Action repair** — `ActionFlags.repair_malformed_actions`
(`AgentLab/src/agentlab/agents/dynamic_prompting.py`: `ActionPrompt._parse_answer`,
`repair_action_answer`, `_first_call`)

- Runs only after the regular parser has rejected an answer. Every answer the regular parser
  accepts is processed exactly as before.
- Recovers the action in two cases only:
  - `tool_call`: the answer has no `<action>` tag, and an action call
    (`click(…)`, `goto(…)`, …, from the benchmark's action set) directly follows a `<tool_call>`
    tag. The call is cut at its matching closing parenthesis (quotes and escapes respected), so
    trailing junk and a missing `</tool_call>` do not matter.
  - `duplicate_action_tags`: several `<action>` tags that all contain the same action. The regular
    parser merges them into a multi-action, which the single-action set rejects.
- The recovered action is then validated by the action set exactly like a regular one
  (`action_set.to_python_code`); if it is invalid, the original parse error stands and the normal
  retry follows.
- Deliberately not repaired, because the intended action would be a guess:
  - several `<action>` tags with different actions (one answer copied the whole action history
    with 38 tags; taking the first would replay an old action);
  - an action call mentioned in prose without a tag (it may be part of the reasoning, not a
    decision);
  - calls that are not valid Python, e.g. `goto(url: '…')`;
  - text between `<tool_call>` and the call, e.g. `<tool_call>$action\ngoto(…)`.
- The prompt, the action space, the examples and the instructions shown to the model are
  unchanged.

**2. Retry from the original prompt** — `GenericPromptFlags.add_missparsed_messages = False`
(`AgentLab/src/agentlab/llm/llm_utils.py`: `retry`; `generic_agent.py`: `get_action`)

- AgentLab already declared this flag ("When retrying, add the missparsed messages to the
  prompt") but never read it; it is now implemented. With `False`, every retry sends the original
  system and user message again, so the model draws a fresh answer (temperature 1) without seeing
  its malformed one.
- The number of retries (4) and the episode ending after the 4th failure are unchanged.
- Failed answers and error messages are still recorded in the step's `chat_messages`, so the logs
  and AgentLab's `n_retry` statistic are unchanged.
- This restores the retry half of H2, which had been reverted with H6.

**3. Measurement** (`generic_agent.py`: `get_action`)

- Every step records `stats.n_repair_tool_call` and `stats.n_repair_duplicate_action_tags`
  (0/1, summed per episode as `cum_…` in `summary_info.json`) and `extra_info.parse_repair`.
- Format errors therefore remain measurable after the change: a repaired answer is still a format
  error, it just no longer costs a retry or the episode. Together with `n_retry` and
  `busted_retry`, this allows reporting the format-error rate per condition, which is itself a
  result (skill text increases format drift).

**4. Configuration** (`run_webmall_study.py`)

```python
FLAGS_AX_M.action.repair_malformed_actions = True
FLAGS_AX_M.add_missparsed_messages = False
```

### Why this is a legitimate change, not tuning toward a result

- It fixes how the harness reads the model's answer; it does not change what the model is asked,
  what it may do, or how the result is scored. Tolerant output parsing is common in LLM-agent
  harnesses, since the benchmark is meant to measure task ability rather than adherence to one
  output syntax.
- It applies identically to all conditions (no skill, base, lite, SkillOpt), and only to answers
  the original parser rejected.
- The repaired actions are exactly what the model wrote, just in a different wrapper; no new
  information is added and nothing is inferred.
- Its effect is logged per step, so the format errors are reported, not hidden.
- It keeps the deviation from the original WebMall setup minimal (see H6 for why the original
  setup is the reference): both options are off by default, the prompt and evaluation are
  untouched, and H3's other changes (reasoning re-inserted as `<think>`, the 1,000-character
  think cap) are not restored. It was added only after the GLM runs showed that the original
  parsing ends episodes because of answer syntax, which the benchmark is not meant to measure.
- Caveat to state in the thesis: the change was motivated by results on the test split. To limit
  test-set reuse, its effect is verified offline (replay) and on train tasks, and the test split is
  used once more only for the final, frozen evaluation.

### Evidence: offline replay (no API calls)

`task_results/2026-11-17_parser_replay/replay_parser.py` re-parses logged answers with the old
and the new parser (`replay_summary.md`, `replay_results.json`):

| Run | Episodes | Failed answers repaired | Episodes that ended on the format | …would not have ended (repair alone) | Accepted answers unchanged |
|---|---|---|---|---|---|
| no skill (test, 19-04-34) | 33 | 22 / 41 | 0 | – | 884 / 884 |
| no skill (test, rerun8) | 8 | 7 / 14 | 0 | – | 228 / 228 |
| lite (test) | 33 | 36 / 134 | 8 | 6 | 701 / 701 |
| optimized (test) | 33 | 76 / 100 | 17 | 17 | 353 / 353 |
| SkillOpt glm_lite (train+val) | 137 | 160 / 439 | 39 | 35 | 2430 / 2430 |
| **total** | 244 | **301 / 728 (41 %)** | **64** | **58** | **4596 / 4596** |

- 58 of the 64 episode endings would not have happened with the repair alone. The remaining
  failures are prose-only or empty answers, which the retry change addresses.
- None of the 4,596 answers the old parser accepted is parsed differently (regression check), and
  none of the 728 failed answers is accepted by the old parser on replay (sanity check).
- Repaired actions: click 137, goto 121, fill 25, go_back 6, scroll 6, select_option 3,
  keyboard_press 3.
- Limitation: the replay shows which steps would have continued, not how the episodes would have
  ended; that needs new runs. The retry change cannot be replayed offline (it needs new samples).

### Tests

- `AgentLab/tests/agents/test_generic_prompt.py`: real failing GLM answers (shortened) as cases —
  repaired ones (unclosed `<tool_call>`, `</arg_value>` junk, keyword arguments with parentheses
  inside the URL, identical duplicate tags), unrepaired ones (empty, prose, different actions,
  non-Python call, unclosed call, call not directly after the tag), and a valid answer that must be
  parsed identically with and without the option.
- `AgentLab/tests/llm/test_llm_utils.py`: with `add_missparsed_messages=True` each retry sees the
  failed answers; with `False` each retry sends only the original prompt; all attempts are logged
  either way.
- End-to-end check of `GenericAgent.get_action` with a stub model (no API): a `<tool_call>` answer
  is accepted without a retry and counted in `n_repair_tool_call`; prose answers are retried with
  the 2 original messages each, 7 messages are logged and `n_retry = 2`.
- Result: 39 passed. (`tests/agents/test_agent.py` needs a MiniWoB server and fails with and
  without this change.)

### Still to do before the final runs

- Short validation run on train tasks (not test) to confirm aborts drop to about 0 online.
- ~~Commit the AgentLab change and bump the submodule~~: AgentLab `4350801` on `revert-reasoning-retry`.
- Freeze the setup (H11 plus the open setup decisions below) for all final runs.

---

## Earlier changes (H1–H10)

### H1 — OpenRouter pricing parsing (AgentLab `42e3f67`, 2026-10-01)
OpenRouter's model list contains non-numeric pricing fields; parsing them crashed the cost
tracker. They are now skipped. Affects cost accounting only.

### H2 — Retry from the original prompt, `""` for empty content (AgentLab `6d88946`, 2026-10-20) — reverted by H6
`retry()` resent the original prompt on every attempt, because deepseek-v4.1-flash copied
malformed answers it saw in its context (19 % of first answers malformed, 73–82 % of the 3rd and
4th retries; episodes ended with nothing submitted). Also turned `content=None` into `""`.
Both parts were reverted on 2026-11-05 (H6) and later restored separately (H8, H11).

### H3 — DeepSeek answer parsing and reasoning as `<think>` (AgentLab `3172f15`, 2026-10-22) — reverted by H6
- Single-action sets took the first `<action>` block instead of merging repeated blocks
  (deepseek-v4.1-flash often repeated its whole answer; 19 of 33 test episodes aborted).
- The model's separate reasoning field was put back into the answer as `<think>`.
- Past thoughts in the history were cut to their last 1,000 characters, because full reasoning
  (2–20k characters per step) filled the prompt and forced the current page tree to be truncated.

H11 does not restore the `<think>` re-insertion or the 1,000-character cap, and restores the
first-`<action>` rule only in the strict form "all tags identical".

### H4 — OpenRouter provider routing and reported cost (AgentLab `b0dc191`, 2026-10-22)
`OpenRouterModelArgs.provider` is sent as OpenRouter's `provider` field; our GLM configuration uses
`{"sort": "price"}` (cheapest provider first, fallbacks allowed). Cost is taken from OpenRouter's
reported cost instead of a price table. See "Open setup decisions" for the consequence.

### H5 — Error report with pandas 3 (AgentLab `fd9b03c`, 2026-10-26)
pandas 3 stores missing error messages as NaN instead of None, which crashed AgentLab's result
analysis before `result_df.csv`, `summary_df.csv` and `error_report.md` were written. Analysis only.

### H6 — Revert of H2 and H3 (AgentLab `25d8183`, `33c6adc`, 2026-11-05)
Returned answer parsing, retries and the handling of reasoning to AgentLab's upstream behaviour
before the GLM runs of 2026-11-05.
Reason: the experiments should be based on the original WebMall benchmark setup as closely as
possible, and H2/H3 had been made for deepseek-v4.1-flash, which is no longer used; there was no
evidence at the time that they were needed for GLM 5.3 Flash.
H8 and H11 later restored parts of H2/H3, each only after the GLM runs showed the same problem
(H8: crashes on empty answers; H11: episodes ended by malformed answers and self-repeating
retries), and H11 as opt-in options whose use is logged per step, so the deviation from the
original setup is explicit and measurable.
Measured side effect on the no-skill GLM test run (2026-10-25 with H2/H3 vs. 2026-11-05 without,
confounded with H8–H10 and sampling noise): output tokens per task 74k → 41.5k, cost per task
$0.035 → $0.023.

### H7 — OpenRouter reasoning option (AgentLab `5d3cc37`, 2026-11-05)
`OpenRouterModelArgs.reasoning` is sent as the request's `reasoning` field, e.g.
`{"effort": "low"}`. Not set for GLM so far (see "Open setup decisions").

### H8 — `content=None` becomes `""` (AgentLab `5472ea4`, 2026-11-05)
GLM 5.3 Flash can end its turn after its reasoning with no answer text (`content=None`). The
parser then failed with a `TypeError` that aborted the episode (3 of 33 test episodes:
Find_Compatible_Products_Task1, EndToEnd_Task1, Find_Substitutes_Task5). With `""`, the empty
answer is an ordinary parse error that the retry handles. Restores this part of H2.

### H9 — WebMall evaluator waits for pending requests and navigations (BrowserGym `53a84e8`, 2026-11-05)
The task's `validate()` ran right after BrowserGym considered an action done, while a navigation
started by the action could still be in flight:
- `page.content()` failed with "page is navigating" and aborted the episode
  (all 3 Add_To_Cart test tasks, after clicking a search button);
- WooCommerce's AJAX checkout redirects to the order-received page only after its request
  returns, so the evaluator saw `/checkout/` and did not credit placed orders
  (Checkout_Task3, EndToEnd_Task2).

The task now tracks the browser context's in-flight document/XHR/fetch requests and waits until
none has been pending for 500 ms (at most 10 s), then for the page load, before evaluating;
`page.content()` is retried while the page is navigating. Playwright's "networkidle" was not
sufficient because it does not cover requests made after a navigation. Adds about 0.5 s per step.
Verified by rerunning the 8 affected tasks (no crashes, all checkouts credited, the 10 s limit was
never reached) and a synthetic Playwright page that redirects after an AJAX request.
This changes scoring only where the old evaluator was wrong (it missed orders that were placed).

### H10 — 5 parallel jobs (this repo, `6d05853`, 2026-11-05)
Studies run 5 episodes in parallel (Ray) instead of one, reducing a 33-task test run from about
9 h to about 1.5 h. SkillOpt rollouts use the same (`env.n_jobs=5`). Side effect: more click
timeouts under load (action errors per task 2.4 sequential vs. 10.2 parallel in the no-skill test
runs); these are recoverable action errors, not episode endings, and affect all conditions alike.

---

## Open setup decisions (to fix before the final runs)

| Setting | Current | Issue |
|---|---|---|
| Provider | `{"sort": "price"}`: cheapest first, fallbacks on | All GLM runs so far went to Relace, which serves the model in fp4 (strongly quantized). The provider can change between runs, which hurts reproducibility, and quantization may contribute to format drift. Option: pin one provider without fallbacks. |
| Reasoning effort | not set → provider default `max` | Should be stated explicitly. `low`/`high` would cut cost and time but change the agent. |
| Runs per task | 1 | One task decides many comparisons; at least 3 runs per condition for confidence intervals. |
| SkillOpt validation repeats | `val_repeats: 1` | The gate selected a skill that aborted 10 % of validation but 52 % of test episodes; repeats make the gate less noise-driven. |
| Gold labels | as published | Some expected answers look wrong (Xbox, PSU tasks); decide whether to correct, exclude or only report them. |
