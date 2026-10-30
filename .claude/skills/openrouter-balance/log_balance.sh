#!/usr/bin/env bash
# Appends the API key's remaining balance (limit minus usage) to budget_history.md and computes the
# cost as the drop from the previous entry's balance. Usage: log_balance.sh "what ran"
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
history="$root/budget_history.md"
note="${1:-}"

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -f "$root/.env" ]; then
  OPENROUTER_API_KEY="$(grep -E '^[[:space:]]*(export[[:space:]]+)?OPENROUTER_API_KEY=' "$root/.env" | tail -1 | sed -E 's/^[^=]*=//; s/^["'\'']//; s/["'\'']$//')"
fi
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "OPENROUTER_API_KEY not found in env or .env" >&2; exit 1; }

key="$(curl -sf -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/key)" \
  || { echo "Key request failed" >&2; exit 1; }

python3 - "$key" "$history" "$note" <<'PY'
import json, os, re, sys
from datetime import datetime

k = json.loads(sys.argv[1]).get("data") or sys.exit("No key data returned from OpenRouter")
path, note = sys.argv[2], sys.argv[3].replace("|", "/")
if k.get("limit_remaining") is None:
    sys.exit("This key has no credit limit, so it has no balance to track")
balance = k["limit_remaining"]

header = ("# OpenRouter Budget History\n\n"
          "Remaining balance of this project's API key (limit minus usage), logged after every "
          "command that calls OpenRouter; cost is the drop from the previous balance.\n\n"
          "| Timestamp | Balance ($) | Cost since previous ($) | Note |\n"
          "|---|---|---|---|\n")
if not os.path.exists(path):
    with open(path, "w") as f:
        f.write(header)

prev = None
for line in open(path):
    m = re.match(r"\|\s*[^|]+\|\s*(-?[0-9][0-9.,]*)\s*\|", line)
    if m:
        prev = float(m.group(1).replace(",", ""))

cost = f"{prev - balance:.4f}" if prev is not None else "n/a (first entry)"
ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
with open(path, "a") as f:
    f.write(f"| {ts} | {balance:.4f} | {cost} | {note} |\n")
print(f"Balance ${balance:,.4f}; cost since previous entry: {cost}")
PY
