# WebMall-Skills

## Results always go in this repo

Every run result (AgentLab experiment directories, console logs, summaries) must be written to
or copied into this repo, never left only in a temp or job folder (`/tmp`, `$CLAUDE_JOB_DIR`,
...), which gets deleted.

- Ad-hoc and single-task runs: `task_results/` (pass it as `study_dir`), with the console log
  next to the run directories.
- SkillOpt runs (probe, C3, test_eval): `skillopt_results/`, where those commands write by default.

## Log the OpenRouter budget after every API call

After every command that makes OpenRouter API calls (task runs, studies, SkillOpt runs, ad-hoc
LLM scripts), and also when such a command fails or is interrupted, append the current balance
to `budget_history.md` in the repo root:

```bash
.claude/skills/openrouter-balance/log_balance.sh "<what ran, e.g. run_single_task webmall.Webmall_Single_Task_1>"
```

The script fetches the remaining balance of this project's API key (`limit_remaining` from
`/api/v1/key`, not the account-wide balance) and records the cost as the drop from the previous
entry's balance. Never edit past rows by hand; report the logged cost to the user.
If several commands ran back to back, log once after each one so costs stay attributable.
