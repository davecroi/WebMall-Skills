# Test split — held-out evaluation

33 test tasks of `skillopt_webmall/split_v2` (never seen by SkillOpt), ×1 run per skill, Luna, 50 steps. Env errors score 0. Missing = not run yet.

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| best (C3 v0007) | 33 | 0.824 | 0.727 | 0 | 0 |
| base skill | 33 | 0.840 | 0.758 | 0 | 0 |
| no skill | 33 | 0.820 | 0.697 | 0 | 0 |

## Per category

| Category | best (C3 v0007) F1 | base skill F1 | no skill F1 |
|---|---|---|---|
| Specific_Product | 1.000 | 1.000 | 1.000 |
| Cheapest_Product | 1.000 | 1.000 | 0.667 |
| Best_Fit_Specific | 1.000 | 1.000 | 0.889 |
| Best_Fit_Vague | 0.861 | 0.826 | 0.886 |
| Cheapest_Best_Fit_Specific | 0.333 | 0.333 | 0.333 |
| Cheapest_Best_Fit_Vague | 0.784 | 0.583 | 0.748 |
| Add_To_Cart | 1.000 | 1.000 | 1.000 |
| Compatible_Products | 0.752 | 0.833 | 0.833 |
| Substitute | 0.667 | 0.667 | 0.667 |
| Checkout | 1.000 | 1.000 | 1.000 |
| FindAndOrder | 0.667 | 1.000 | 1.000 |

## Efficiency

Mean per test run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| best (C3 v0007) | 27.2 | 246,280 | 6,749 | 0.0280 | 179 | 2 |
| base skill | 27.1 | 224,363 | 6,095 | 0.0255 | 168 | 1 |
| no skill | 22.7 | 183,216 | 5,704 | 0.0212 | 172 | 0 |
| Δ best (C3 v0007) vs. base skill | +0.2 (+1%) | +21,917 (+10%) | +654 (+11%) | +0.0025 (+10%) | +12 (+7%) | +1 |
| Δ best (C3 v0007) vs. no skill | +4.5 (+20%) | +63,065 (+34%) | +1,045 (+18%) | +0.0068 (+32%) | +7 (+4%) | +2 |
| Δ base skill vs. no skill | +4.4 (+19%) | +41,147 (+22%) | +391 (+7%) | +0.0043 (+20%) | -4 (-3%) | +1 |

Totals: best (C3 v0007) $0.92 / 5917 s (99 min); base skill $0.84 / 5535 s (92 min); no skill $0.70 / 5677 s (95 min).

## Per task

Δ = best (C3 v0007) − base skill.

| Task | Category | best (C3 v0007) F1 | base skill F1 | no skill F1 | Δ best (C3 v0007) − base skill | best (C3 v0007) steps | base skill steps | no skill steps |
|---|---|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task3 | Specific_Product | 1.000 | 1.000 | 1.000 | +0.000 | 37 | 30 | 21 |
| Webmall_Find_Specific_Product_Task9 | Specific_Product | 1.000 | 1.000 | 1.000 | +0.000 | 20 | 20 | 26 |
| Webmall_Find_Specific_Product_Task10 | Specific_Product | 1.000 | 1.000 | 1.000 | +0.000 | 19 | 19 | 9 |
| Webmall_Find_Cheapest_Offer_Task3 | Cheapest_Product | 1.000 | 1.000 | 1.000 | +0.000 | 28 | 25 | 19 |
| Webmall_Find_Cheapest_Offer_Task9 | Cheapest_Product | 1.000 | 1.000 | 1.000 | +0.000 | 20 | 15 | 15 |
| Webmall_Find_Cheapest_Offer_Task5 | Cheapest_Product | 1.000 | 1.000 | 0.000 | +0.000 | 17 | 14 | 14 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task10 | Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 35 | 27 | 41 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task1 | Best_Fit_Specific | 1.000 | 1.000 | 0.667 | +0.000 | 24 | 22 | 14 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task3 | Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 29 | 24 | 18 |
| Webmall_Products_Satisfying_Vague_Requirements_Task1 | Best_Fit_Vague | 1.000 | 1.000 | 1.000 | +0.000 | 19 | 19 | 23 |
| Webmall_Products_Satisfying_Vague_Requirements_Task7 | Best_Fit_Vague | 0.727 | 0.727 | 0.800 | +0.000 | 33 | 36 | 32 |
| Webmall_Products_Satisfying_Vague_Requirements_Task8 | Best_Fit_Vague | 0.857 | 0.750 | 0.857 | +0.107 | 37 | 39 | 26 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task1 | Cheapest_Best_Fit_Specific | 0.000 | 0.000 | 0.000 | +0.000 | 19 | 19 | 18 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task8 | Cheapest_Best_Fit_Specific | 0.000 | 0.000 | 0.000 | +0.000 | 23 | 22 | 18 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task5 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 21 | 21 | 19 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task6 | Cheapest_Best_Fit_Vague | 1.000 | 0.750 | 0.800 | +0.250 | 29 | 35 | 13 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task4 | Cheapest_Best_Fit_Vague | 0.353 | 0.000 | 0.444 | +0.353 | 50 | 50 | 42 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task1 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | 1.000 | +0.000 | 40 | 40 | 43 |
| Webmall_Add_To_Cart_Task4 | Add_To_Cart | 1.000 | 1.000 | 1.000 | +0.000 | 17 | 26 | 17 |
| Webmall_Add_To_Cart_Task3 | Add_To_Cart | 1.000 | 1.000 | 1.000 | +0.000 | 24 | 27 | 17 |
| Webmall_Add_To_Cart_Task5 | Add_To_Cart | 1.000 | 1.000 | 1.000 | +0.000 | 25 | 35 | 32 |
| Webmall_Find_Compatible_Products_Task3 | Compatible_Products | 0.857 | 1.000 | 1.000 | -0.143 | 26 | 24 | 23 |
| Webmall_Find_Compatible_Products_Task5 | Compatible_Products | 1.000 | 1.000 | 1.000 | +0.000 | 11 | 15 | 10 |
| Webmall_Find_Compatible_Products_Task1 | Compatible_Products | 0.400 | 0.500 | 0.500 | -0.100 | 32 | 36 | 19 |
| Webmall_Find_Substitutes_Task5 | Substitute | 1.000 | 1.000 | 1.000 | +0.000 | 24 | 28 | 12 |
| Webmall_Find_Substitutes_Task2 | Substitute | 1.000 | 1.000 | 1.000 | +0.000 | 17 | 18 | 17 |
| Webmall_Find_Substitutes_Task1 | Substitute | 0.000 | 0.000 | 0.000 | +0.000 | 23 | 14 | 11 |
| Webmall_Checkout_Task7 | Checkout | 1.000 | 1.000 | 1.000 | +0.000 | 23 | 23 | 22 |
| Webmall_Checkout_Task2 | Checkout | 1.000 | 1.000 | 1.000 | +0.000 | 23 | 23 | 23 |
| Webmall_Checkout_Task3 | Checkout | 1.000 | 1.000 | 1.000 | +0.000 | 22 | 21 | 23 |
| Webmall_EndToEnd_Task7 | FindAndOrder | 0.000 | 1.000 | 1.000 | -1.000 | 50 | 49 | 48 |
| Webmall_EndToEnd_Task2 | FindAndOrder | 1.000 | 1.000 | 1.000 | +0.000 | 38 | 36 | 28 |
| Webmall_EndToEnd_Task1 | FindAndOrder | 1.000 | 1.000 | 1.000 | +0.000 | 44 | 42 | 37 |
