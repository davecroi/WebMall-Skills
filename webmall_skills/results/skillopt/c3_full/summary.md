# C3 run summary — c3_full

Split `skillopt_webmall/split_v2`, 21 val tasks × 1, 4 epochs, gate `soft` (mean per-task F1). Status: **finished**.

## Steps

Train F1 = mean over the step's train batch; patches = minibatches the optimizer reflected on (failure / success); Δ = candidate val F1 − val F1 of the skill it tried to replace.

| Step | Epoch | Train F1 | Patches (fail / succ) | Edits | Cand. val F1 | Cand. val CR | Δ | Decision | Cost ($) | Time (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 0.817 | 1 / 3 | 4 | 0.610 | 0.571 | -0.095 | rejected (gate) | 1.08 | 102 |
| 2 | 1 | 0.805 | 1 / 2 | 4 | 0.787 | 0.667 | +0.082 | accepted ★ | 1.02 | 98 |
| 3 | 2 | 0.679 | 2 / 2 | 3 | 0.638 | 0.571 | -0.150 | rejected (gate) | 1.13 | 103 |
| 4 | 2 | 0.908 | 1 / 1 | 3 | 0.595 | 0.571 | -0.192 | rejected (gate) | 1.01 | 93 |
| 5 | 3 | 0.944 | 1 / 2 | 3 | 0.793 | 0.714 | +0.005 | accepted ★ | 1.01 | 90 |
| 6 | 3 | 0.795 | 1 / 2 | 2 | 0.667 | 0.667 | -0.126 | rejected (gate) | 1.15 | 99 |
| 7 | 4 | 0.751 | 2 / 1 | 2 | 0.865 | 0.810 | +0.073 | accepted ★ | 1.11 | 96 |
| 8 | 4 | 1.000 | 0 / 1 | 1 | 0.837 | 0.714 | -0.028 | rejected (gate) | 1.08 | 89 |

Training cost so far: $8.59 over 8 steps (base-skill baseline came from the step 0 cache).

## Best skill vs. base skill vs. no skill (val)

Best skill: **v0007** (`steps/step_0007/candidate_skill.md`).

**Caveat:** the best skill was *selected* on these val tasks, so its val score is optimistic. The unbiased comparison is the test split (`webmall_thesis_test_v1.0` in `run_webmall_study.py`), run once per skill.

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| best (v0007) | 21 | 0.865 | 0.810 | 0 | 0 |
| base skill (×1) | 21 | 0.705 | 0.667 | 0 | 0 |
| no skill (×1) | 21 | 0.707 | 0.571 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| best (v0007) | 28.6 | 277,197 | 7,332 | 0.0314 | 156 | 1 |
| base skill (×1) | 30.0 | 271,073 | 7,717 | 0.0310 | 195 | 4 |
| no skill (×1) | 23.1 | 214,548 | 6,302 | 0.0246 | 201 | 1 |
| Δ best vs. base | -1.4 (-5%) | +6,124 (+2%) | -385 (-5%) | +0.0004 (+1%) | -39 (-20%) | -3 |
| Δ best vs. no skill | +5.5 (+24%) | +62,650 (+29%) | +1,030 (+16%) | +0.0068 (+28%) | -45 (-22%) | +0 |

Totals: best $0.66 / 3266 s (54 min); base skill $0.65 / 4086 s (68 min); no skill $0.52 / 4211 s (70 min).

## Per task

F1 and steps per val task (mean over repeats); Δ = best − base.

| Task | Category | best F1 | base F1 | no skill F1 | Δ best − base | best steps | base steps | no skill steps |
|---|---|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 1.000 | 0.000 | 0.308 | +1.000 | 49 | 50 | 17 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | 1.000 | +0.000 | 20 | 24 | 12 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | 1.000 | +0.000 | 17 | 15 | 15 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | 0.000 | +0.000 | 23 | 50 | 31 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 22 | 21 | 17 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 28 | 30 | 19 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 1.000 | 0.000 | 0.714 | +1.000 | 44 | 50 | 35 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.667 | 0.000 | 0.667 | +0.667 | 50 | 50 | 47 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 20 | 19 | 15 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | 1.000 | +0.000 | 21 | 19 | 16 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | 1.000 | +0.000 | 25 | 32 | 21 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | 0.000 | +0.000 | 24 | 25 | 14 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | 1.000 | +0.000 | 18 | 20 | 21 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | 0.667 | +0.000 | 26 | 34 | 16 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.500 | 0.800 | 0.500 | -0.300 | 36 | 19 | 20 |
| Webmall_Find_Substitutes_Task4 | Substitute | 1.000 | 1.000 | 0.000 | +0.000 | 21 | 21 | 13 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | 1.000 | +0.000 | 35 | 29 | 24 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 0.000 | 1.000 | +1.000 | 23 | 26 | 24 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | 1.000 | +0.000 | 22 | 22 | 21 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | 1.000 | +0.000 | 35 | 36 | 38 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | 0.000 | +0.000 | 42 | 38 | 50 |
