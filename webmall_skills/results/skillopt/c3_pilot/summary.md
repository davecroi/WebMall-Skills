# C3 run summary — c3_pilot

Split `skillopt_webmall/split`, 11 val tasks × 2, 1 epochs, gate `soft` (mean per-task F1). Status: **finished**.

## Steps

Train F1 = mean over the step's train batch; patches = minibatches the optimizer reflected on (failure / success); Δ = candidate val F1 − val F1 of the skill it tried to replace.

| Step | Epoch | Train F1 | Patches (fail / succ) | Edits | Cand. val F1 | Cand. val CR | Δ | Decision | Cost ($) | Time (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 0.939 | 1 / 2 | 3 | 0.709 | 0.636 | -0.045 | rejected (gate) | 1.02 | 88 |

Training cost so far: $1.02 over 1 steps (base-skill baseline came from the step 0 cache).

## Best skill vs. base skill vs. no skill (val)

Best skill: **v0000** — no candidate has beaten the base skill, so best = base.

**Caveat:** the best skill was *selected* on these val tasks, so its val score is optimistic. The unbiased comparison is the test split (`webmall_thesis_test_v1.0` in `run_webmall_study.py`), run once per skill.

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| base skill (×2) | 22 | 0.755 | 0.682 | 0 | 0 |
| no skill (×1) | 11 | 0.775 | 0.636 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| base skill (×2) | 28.0 | 261,517 | 7,454 | 0.0299 | 167 | 3 |
| no skill (×1) | 21.5 | 176,096 | 5,302 | 0.0203 | 131 | 0 |
| Δ base vs. no skill | +6.5 (+30%) | +85,420 (+49%) | +2,152 (+41%) | +0.0096 (+47%) | +36 (+28%) | +3 |

Totals: base skill $0.66 / 3683 s (61 min); no skill $0.22 / 1441 s (24 min).

## Per task

F1 and steps per val task (mean over repeats); Δ = base − no skill.

| Task | Category | base F1 | no skill F1 | Δ base − no skill | base steps | no skill steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.308 | -0.308 | 50 | 17 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 15.5 | 15 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 22 | 17 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.500 | 0.714 | -0.214 | 48 | 35 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 20.5 | 15 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 28 | 21 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 20 | 21 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.500 | +0.300 | 23.5 | 20 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.500 | 0.000 | +0.500 | 19.5 | 13 |
| Webmall_Checkout_Task8 | Checkout | 0.500 | 1.000 | -0.500 | 24.5 | 24 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 36 | 38 |
