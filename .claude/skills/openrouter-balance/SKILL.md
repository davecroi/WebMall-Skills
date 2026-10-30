---
name: openrouter-balance
description: Check the OpenRouter account credit balance and current API key usage/limit. Use when the user asks about OpenRouter balance, credits, spend, or remaining budget.
allowed-tools: Bash(.claude/skills/openrouter-balance/check_balance.sh)
---

Run the balance script from the project root and report its output to the user concisely:

```bash
.claude/skills/openrouter-balance/check_balance.sh
```

The script reads `OPENROUTER_API_KEY` from the environment or the project `.env` and never prints the key. It shows:
- **Account balance**: total purchased credits minus total usage (`/api/v1/credits`)
- **This key**: usage, limit, remaining, and daily/monthly spend (`/api/v1/key`)

If the key has a limit and `remaining` is under ~10% of it, call that out.
