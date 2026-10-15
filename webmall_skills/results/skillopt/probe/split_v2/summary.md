# Step 0 — Luna val check (skillopt_webmall/split_v2)

| Condition | Rollouts | Mean F1 | Mean CR | Env-error share |
|---|---|---|---|---|
| base skill (×1) | 21 | 0.705 | 0.667 | 0% |
| no skill (×1) | 21 | 0.707 | 0.571 | 0% |

**Decision:** GO

Cost: $0.62 for 20 rollouts.

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| base skill (×1) | 30.0 | 271,073 | 7,717 | 0.0310 | 195 | 4 |
| no skill (×1) | 23.1 | 214,548 | 6,302 | 0.0246 | 201 | 1 |
| Δ base vs. no skill | +6.9 (+30%) | +56,525 (+26%) | +1,415 (+22%) | +0.0064 (+26%) | -6 (-3%) | +3 |

Totals: base skill $0.65 / 4086 s (68 min); no skill $0.52 / 4211 s (70 min).

## Per task

F1 per val task; Δ = base − no skill. Runs: `new` = run by this probe, `cached` = reused from an earlier probe.

| Task | Category | Base F1 | No-skill F1 | Δ | Base steps | No-skill steps | Base runs | No-skill runs |
|---|---|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.308 | -0.308 | 50 | 17 | cached | cached |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 24 | 12 | new | new |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 15 | 15 | cached | cached |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 50 | 31 | new | new |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 21 | 17 | cached | cached |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 30 | 19 | new | new |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.000 | 0.714 | -0.714 | 50 | 35 | cached | cached |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.667 | -0.667 | 50 | 47 | new | new |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 19 | 15 | cached | cached |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 19 | 16 | new | new |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 32 | 21 | cached | cached |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 25 | 14 | new | new |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 20 | 21 | cached | cached |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 0.667 | +0.333 | 34 | 16 | new | new |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.500 | +0.300 | 19 | 20 | cached | cached |
| Webmall_Find_Substitutes_Task4 | Substitute | 1.000 | 0.000 | +1.000 | 21 | 13 | cached | cached |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 29 | 24 | new | new |
| Webmall_Checkout_Task8 | Checkout | 0.000 | 1.000 | -1.000 | 26 | 24 | cached | cached |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 21 | new | new |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 36 | 38 | cached | cached |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 0.000 | +1.000 | 38 | 50 | new | new |
