# `lite/` — lightweight skill from the GLM test-run failures

`SKILL.md` is a short skill (~570 words, base: 667) written by hand from the failures of two
`z-ai/glm-5.3-flash` runs on the 33-task test split:

| Run | Study | Avg reward | Completion | P / R / F1 |
|---|---|---|---|---|
| No skill | `task_results/2026-10-25_14-34-33_…-on-webmall-skills-test-ax-m` | 0.700 | 0.576 | 0.662 / 0.671 / 0.667 |
| Base skill | `task_results/2026-10-26_12-42-20_…-skill-base-on-webmall-skills-test-ax-m` | 0.520 | 0.424 | 0.466 / 0.488 / 0.477 |

Select it with `skill = "lite"` in `run_webmall_study.py` or `run_single_task.py`.

## Contamination caveat

The rules are derived from **test-split** trajectories, so a `lite` score on `webmall_skills_test` is
not a held-out result. Use the 21-task `webmall_skills_val` split (or train) for an unbiased comparison
against no skill and base. The text names no products, brands, model numbers or URLs:
`python -m webmall_skills.contamination doc webmall_skills/skills/lite/SKILL.md` reports 0 hits. The
`words` report lists generic overlaps only (e.g. *adapter*, *capacity*, *price*).

## Failure → rule

| Failure seen in the runs | Evidence | Rule |
|---|---|---|
| No submission before the step cap (50) or the ~50 min Ray episode timeout | no skill: 5 truncated + 2 timeouts; base: 5 truncated + 4 timeouts | §1 one pass per shop, stop searching by about action 30 |
| Prompt bloat from long think and memory notes | log lines "prompt is still 163053 tokens (greater than 59996)"; base: +42 % output tokens, +32 % time | §1 short `<think>`, ledger-only `<memory>` |
| Submitted URLs that were never opened (invented from titles) | base: 16 of 16 such URLs wrong (Cheapest_Offer_Vague 4 and 6, Find_Cheapest_Offer 3, Cheapest_Offer_Specific 5 with an added `/wordpress/` segment); no skill: 4 of 12 wrong | §2 open each offer, copy the tab URL |
| Correct URL typed in, but **Submit Final Result** never clicked; agent claimed a confirmation | base Find_Specific_Product 10 (no-ops until step 50) | §3 |
| Agent left checkout before `/checkout/order-received` loaded | base EndToEnd 2 (0.2) | §4 |
| Wrong product type or variant, extra listings | Cheapest_Offer_Vague 4 (both runs), Find_Compatible 5 (base), Cheapest_Offer_Vague 6 (no skill), Products_Satisfying_Vague 7 (both runs) | §5 type and variant match, vague → concrete type first |
| A tied offer missed, or the minimum taken from the wrong shop | Find_Cheapest_Offer 9 (no skill), Find_Substitutes 5 (base) | §5 compare all four shops, submit all ties |
| A qualifying offer missed in one shop | Cheapest_Offer_Specific 1 and 8 | §6 shorter queries and synonyms; titles may use other languages or codes |
| Click timeouts on navigating clicks, then needless retries | 60 of 78 (no skill) and 49 of 90 (base) action errors | §6 check the URL before retrying |

Not addressed: Find_Substitutes Task1 has answer type `cart` although its task text asks only for the
offer, so both runs scored 0.2 with the correct URL.
