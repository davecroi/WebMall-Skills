# Test split — held-out evaluation

33 test tasks of `webmall_skills/split/split_v2` (never seen by SkillOpt), ×1 run per skill, Luna, 50 steps. Env errors score 0. Missing = not run yet.

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| no skill | 33 | 0.232 | 0.212 | 0 | 0 |

## Per category

| Category | no skill F1 |
|---|---|
| Specific_Product | 0.000 |
| Cheapest_Product | 0.000 |
| Best_Fit_Specific | 0.000 |
| Best_Fit_Vague | 0.000 |
| Cheapest_Best_Fit_Specific | 0.333 |
| Cheapest_Best_Fit_Vague | 0.000 |
| Add_To_Cart | 0.889 |
| Compatible_Products | 0.000 |
| Substitute | 0.333 |
| Checkout | 0.667 |
| FindAndOrder | 0.333 |

## Efficiency

Mean per test run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| no skill | 28.8 | 370,618 | 136,377 | 0.0237 | 729 | 9 |

Totals: no skill $0.78 / 24049 s (401 min).
