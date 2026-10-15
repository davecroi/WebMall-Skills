# Step 8 (epoch 4) — rejected (gate)

Candidate v0008 vs. parent v0007: val F1 0.837 vs. 0.865; 1 edits applied from 0 failure / 1 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task2 | 1.000 | 1 | 18 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task10 | 1.000 | 1 | 21 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task4 | 1.000 | 1 | 21 |
| Webmall_Checkout_Task1 | 1.000 | 1 | 23 |
| Webmall_Checkout_Task5 | 1.000 | 1 | 23 |
| Webmall_EndToEnd_Task4 | 1.000 | 1 | 47 |
| Webmall_EndToEnd_Task6 | 1.000 | 1 | 40 |
| Webmall_Find_Cheapest_Offer_Task2 | 1.000 | 1 | 28 |
| Webmall_Find_Compatible_Products_Task2 | 1.000 | 1 | 22 |
| Webmall_Find_Specific_Product_Task12 | 1.000 | 1 | 22 |
| Webmall_Find_Specific_Product_Task8 | 1.000 | 1 | 23 |
| Webmall_Find_Substitutes_Task6 | 1.000 | 1 | 26 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task6 | 1.000 | 1 | 25 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0008 | 21 | 0.837 | 0.714 | 0 | 0 |
| parent v0007 | 21 | 0.865 | 0.810 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0008 | 30.0 | 299,396 | 7,864 | 0.0339 | 160 | 2 |
| parent v0007 | 28.6 | 277,197 | 7,332 | 0.0314 | 156 | 1 |
| Δ candidate vs. parent | +1.3 (+5%) | +22,198 (+8%) | +532 (+7%) | +0.0025 (+8%) | +5 (+3%) | +1 |

Totals: candidate $0.71 / 3365 s (56 min); parent $0.66 / 3266 s (54 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.952 | 1.000 | -0.048 | 48 | 49 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 22 | 20 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 16 | 17 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 28 | 23 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 23 | 22 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 28 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.824 | 1.000 | -0.176 | 49 | 44 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.667 | -0.667 | 50 | 50 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 20 | 20 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 22 | 21 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 25 | 25 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 22 | 24 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 18 | 18 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 32 | 26 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.500 | +0.300 | 35 | 36 |
| Webmall_Find_Substitutes_Task4 | Substitute | 1.000 | 1.000 | +0.000 | 35 | 21 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 30 | 35 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 1.000 | +0.000 | 23 | 23 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 21 | 22 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 36 | 35 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 50 | 42 |

## Skill diff (parent → candidate)

```diff
--- v0007.md
+++ v0008.md
@@ -67,5 +67,7 @@
 
 Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.
 
+For cheapest-offer searches, when ascending price order is confirmed, inspect candidates until prices are strictly above the current best; retain every candidate tied at the best price, and later results cannot improve it. If sorting fails or the order is uncertain, do not assume the first page is cheapest or complete—check result counts and remaining pages, or use a focused query.
+
 ## Verify Each Required Attribute
 Qualify each distinct offer only when its own title, specifications, or description provide evidence for every required attribute. Do not infer a feature from a customizable display, a similar product, or another variant in the same product family; for example, an LCD alone does not establish GIF playback. If evidence is unclear, inspect that offer’s product details and keep it out of the final qualifying set unless the requirement is supported.
```
