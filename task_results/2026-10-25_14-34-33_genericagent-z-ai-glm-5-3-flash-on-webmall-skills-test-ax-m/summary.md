# GLM-5.3-flash on WebMall skills test set (33 tasks)

Study: `2026-10-25_14-34-33`, model `z-ai/glm-5.3-flash`, ran 2026-10-25 14:34 to 23:41 CET.
Baseline: DeepSeek v4.1-flash on the same 33 tasks (`2026-10-23_01-04-02`).

| | GLM-5.3-flash | DeepSeek v4.1-flash |
|---|---|---|
| Avg reward | 0.700 | 0.445 |
| Fully solved (1.0) | 20 / 33 | 11 / 33 |
| Tasks with err_msg | 2 | 10 |
| Agent-reported LLM cost | $1.158 | $3.320 |

OpenRouter key balance drop for this run: $1.1641 (`budget_history.md`).

## Avg reward by category

| Category | GLM | DeepSeek |
|---|---|---|
| Add_To_Cart | 0.83 | 1.00 |
| Checkout | 1.00 | 0.73 |
| EndToEnd | 1.00 | 0.07 |
| Find_Specific_Product | 1.00 | 0.71 |
| Find_Cheapest_Offer | 0.73 | 0.43 |
| Find_Substitutes | 0.73 | 0.40 |
| Cheapest_Offer_Vague_Requirements | 0.85 | 0.38 |
| Cheapest_Offer_Specific_Requirements | 0.33 | 0.33 |
| Find_Compatible_Products | 0.41 | 0.41 |
| Products_Fulfilling_Specific_Requirements | 0.43 | 0.10 |
| Products_Satisfying_Vague_Requirements | 0.38 | 0.33 |

## Notes

- Both errors (Add_To_Cart Task3 and Task4) are `KeyboardInterrupt` cutoffs after about 50 min of wall
  time (Task3 ran 19:51 to 20:42), which matches the Ray per-episode timeout. Task3 had already earned 1.0,
  Task4 stopped at 0.5.
- Weak spots: 5 tasks used the full 50 steps with low rewards (Find_Compatible_Products Task1/3,
  Products_Fulfilling_Specific_Requirements Task1/10, Products_Satisfying_Vague_Requirements Task8).
  Cheapest_Offer_Specific_Requirements Task1/8 and Products_Satisfying_Vague_Requirements Task7 scored 0
  for both models.
- The console log was not saved; output went to the terminal only.
