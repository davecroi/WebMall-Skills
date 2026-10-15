# Step 6 (epoch 3) — rejected (gate)

Candidate v0006 vs. parent v0005: val F1 0.667 vs. 0.793; 2 edits applied from 1 failure / 2 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task2 | 1.000 | 1 | 18 |
| Webmall_Add_To_Cart_Task7 | 1.000 | 1 | 25 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task10 | 1.000 | 1 | 21 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task4 | 1.000 | 1 | 26 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task6 | 0.000 | 0 | 29 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task3 | 0.667 | 0 | 25 |
| Webmall_Checkout_Task1 | 1.000 | 1 | 24 |
| Webmall_Checkout_Task4 | 1.000 | 1 | 23 |
| Webmall_EndToEnd_Task4 | 1.000 | 1 | 41 |
| Webmall_EndToEnd_Task8 | 0.000 | 0 | 50 |
| Webmall_Find_Specific_Product_Task8 | 1.000 | 1 | 20 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task8 | 0.667 | 0 | 49 |
| Webmall_Products_Satisfying_Vague_Requirements_Task6 | 1.000 | 1 | 32 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0006 | 21 | 0.619 | 0.619 | 1 | 0 |
| parent v0005 | 21 | 0.793 | 0.714 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0006 | 29.3 | 290,706 | 7,757 | 0.0329 | 166 | 4 |
| parent v0005 | 28.3 | 264,277 | 7,263 | 0.0301 | 154 | 1 |
| Δ candidate vs. parent | +1.0 (+3%) | +26,429 (+10%) | +494 (+7%) | +0.0029 (+10%) | +12 (+8%) | +3 |

Totals: candidate $0.69 / 3487 s (58 min); parent $0.63 / 3228 s (54 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 0.500 | +0.500 | 22 | 22 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 15 | 17 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 39 | 42 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 23 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 22 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.000 | 0.571 | -0.571 | 50 | 29 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.571 | -0.571 | 50 | 45 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 20 | 17 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 19 | 28 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 26 | 27 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 27 | 25 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 20 | 21 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 26 | 27 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.000 | 1.000 | -1.000 | 50 | 27 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.000 | 1.000 | -1.000 | 16 | 21 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 30 | 27 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 1.000 | +0.000 | 25 | 23 |
| Webmall_Checkout_Task6 | Checkout | 0.000 | 1.000 | -1.000 | 8 | 23 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 35 | 37 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 39 | 42 |

## Skill diff (parent → candidate)

```diff
--- v0005.md
+++ v0006.md
@@ -64,4 +64,8 @@
 Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.
 
 ## Verify Each Required Attribute
-Qualify each distinct offer only when its own title, specifications, or description provide evidence for every required attribute. Do not infer a feature from a customizable display, a similar product, or another variant in the same product family; for example, an LCD alone does not establish GIF playback. If evidence is unclear, inspect that offer’s product details and keep it out of the final qualifying set unless the requirement is supported.
+Qualify each distinct offer only when its own title, specifications, or description provide evidence for every required attribute. Distinguish a product having a feature from merely supporting an accessory or add-on that provides it: a header, connector, or compatibility claim alone does not prove the feature is included. Do not infer a feature from a customizable display, a similar product, or another variant in the same product family; for example, an LCD alone does not establish GIF playback. If evidence is unclear, inspect that offer’s product details and keep it out of the final qualifying set unless the requirement is supported.
+
+## Complete Multi-Shop Purchases
+
+For an end-to-end task with selected offers from different shops, group the chosen items by shop. Add all selected items for one shop to that shop’s cart and complete its checkout; repeat for each other shop. Before navigating away from a shop, verify its order-received confirmation. Complete every required order before navigating to the solution page and submitting the exact selected offer URLs.
```
