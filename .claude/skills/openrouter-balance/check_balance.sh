#!/usr/bin/env bash
# Prints OpenRouter credit balance and current key usage. Reads OPENROUTER_API_KEY
# from the environment, falling back to the project's .env.
set -euo pipefail

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  env_file="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.env"
  if [ -f "$env_file" ]; then
    OPENROUTER_API_KEY="$(grep -E '^[[:space:]]*(export[[:space:]]+)?OPENROUTER_API_KEY=' "$env_file" | tail -1 | sed -E 's/^[^=]*=//; s/^["'\'']//; s/["'\'']$//')"
  fi
fi
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "OPENROUTER_API_KEY not found in env or .env" >&2; exit 1; }

auth="Authorization: Bearer $OPENROUTER_API_KEY"
credits="$(curl -sf -H "$auth" https://openrouter.ai/api/v1/credits)" || { echo "Credits request failed (management key may be required)" >&2; credits='{}'; }
key="$(curl -sf -H "$auth" https://openrouter.ai/api/v1/key)" || key='{}'

python3 - "$credits" "$key" <<'PY'
import json, sys
c = json.loads(sys.argv[1]).get("data", {})
k = json.loads(sys.argv[2]).get("data", {})
if c:
    total, used = c.get("total_credits", 0), c.get("total_usage", 0)
    print(f"Account balance: ${total - used:,.4f}  (purchased ${total:,.2f}, used ${used:,.4f})")
if k:
    lim = k.get("limit")
    print(f"This key ({k.get('label', '?')}): usage ${k.get('usage', 0):,.4f}"
          + (f", limit ${lim:,.2f}, remaining ${k.get('limit_remaining', 0):,.4f}" if lim is not None else ", no limit")
          + (f"  | today ${k['usage_daily']:,.4f}, month ${k['usage_monthly']:,.4f}" if 'usage_daily' in k else ""))
if not c and not k:
    sys.exit("No data returned from OpenRouter")
PY
