# GLM-5.3-flash + base skill on WebMall skills test set (33 tasks)

Study: `2026-10-26_12-42-20`, model `z-ai/glm-5.3-flash`, skill `webmall_skills/skills/base/SKILL.md`.
Baseline: same model without skill (`2026-10-25_14-34-33`).

| | No skill | Base skill |
|---|---|---|
| Avg reward | 0.700 | 0.520 |
| Fully solved (1.0) | 20 / 33 | 16 / 33 |
| Task completion rate | 0.576 | 0.424 |
| Precision | 0.662 | 0.466 |
| Recall | 0.671 | 0.488 |
| F1 | 0.667 | 0.477 |
| Tasks with err_msg (all Ray timeouts) | 2 | 4 |
| Avg agent time per task | 893 s | 1175 s |
| Avg input / output tokens per task | 596k / 74k | 813k / 105k |
| Agent-reported LLM cost | $1.158 | $1.315 |

OpenRouter key balance drop for this run: $1.3300 (`budget_history.md`).

## Per-task changes

Better with skill (4): Add_To_Cart Task4 (0.5 -> 1), Cheapest_Offer_Vague_Requirements Task1 (0.8 -> 1),
Find_Cheapest_Offer Task9 (0.2 -> 1), Find_Compatible_Products Task3 (0.15 -> 1).

Worse with skill (12): Cheapest_Offer_Specific_Requirements Task5, Cheapest_Offer_Vague_Requirements Task4/6,
EndToEnd Task2/7, Find_Cheapest_Offer Task3, Find_Compatible_Products Task1, Find_Specific_Product Task10,
Find_Substitutes Task5, Products_Fulfilling_Specific_Requirements Task1/3/10.

## Notes

- The regressions are mostly wrong picks, not format problems: e.g. Find_Cheapest_Offer Task3 submitted a
  Galaxy S24 Plus 128 GB instead of the two S24 5G offers, Find_Substitutes Task5 picked the RTX 4060 on
  shop 8081 instead of 8084.
- With the skill the agent reasons longer per step (+42% output tokens, +32% time), so more tasks hit the
  ~50 min Ray episode timeout (EndToEnd Task7, Products_Fulfilling_Specific_Requirements Task3/10).
- Single run per condition at temperature 1; std err of avg reward is ~0.08 per run, so per-task flips are
  noisy, but 12 down vs 4 up is a consistent negative signal.
