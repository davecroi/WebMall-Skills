# Step 3 (epoch 2) — rejected (gate)

Candidate v0003 vs. parent v0002: val F1 0.638 vs. 0.787; 3 edits applied from 2 failure / 2 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Cheapest_Offer_Specific_Requirements_Task4 | 0.000 | 0 | 17 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task6 | 0.000 | 0 | 50 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task3 | 0.000 | 0 | 22 |
| Webmall_Checkout_Task1 | 1.000 | 1 | 23 |
| Webmall_Checkout_Task4 | 1.000 | 1 | 23 |
| Webmall_Checkout_Task5 | 1.000 | 1 | 23 |
| Webmall_EndToEnd_Task4 | 1.000 | 1 | 40 |
| Webmall_EndToEnd_Task8 | 0.667 | 0 | 50 |
| Webmall_Find_Cheapest_Offer_Task2 | 1.000 | 1 | 29 |
| Webmall_Find_Specific_Product_Task12 | 1.000 | 1 | 18 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task4 | 0.154 | 0 | 35 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task6 | 1.000 | 1 | 39 |
| Webmall_Products_Satisfying_Vague_Requirements_Task6 | 1.000 | 1 | 25 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0003 | 21 | 0.590 | 0.524 | 1 | 0 |
| parent v0002 | 21 | 0.787 | 0.667 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0003 | 28.8 | 277,451 | 7,525 | 0.0315 | 166 | 2 |
| parent v0002 | 27.7 | 244,543 | 6,559 | 0.0277 | 159 | 1 |
| Δ candidate vs. parent | +1.0 (+4%) | +32,908 (+13%) | +966 (+15%) | +0.0038 (+14%) | +7 (+4%) | +1 |

Totals: candidate $0.66 / 3490 s (58 min); parent $0.58 / 3343 s (56 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.842 | -0.842 | 50 | 49 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 22 | 25 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 19 | 15 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 34 | 29 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 23 | 22 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 24 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.889 | 0.889 | +0.000 | 46 | 48 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 0.000 | 1.000 | -1.000 | 21 | 26 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 18 | 23 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 27 | 24 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 22 | 24 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 21 | 18 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 22 | 21 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.500 | 0.800 | -0.300 | 41 | 22 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.000 | 1.000 | -1.000 | 29 | 19 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 22 | 20 |
| Webmall_Checkout_Task8 | Checkout | 0.000 | 1.000 | -1.000 | 9 | 25 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 22 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 35 | 38 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 47 | 38 |

## Skill diff (parent → candidate)

```diff
--- v0002.md
+++ v0003.md
@@ -53,8 +53,16 @@
 
 ## Cross-Shop Coverage for Complete and Tied Results
 
-For tasks asking for all qualifying offers or every offer tied at a maximum, keep a per-shop ledger of candidates, specifications, and exact offer URLs. After identifying a plausible product, search its distinctive model name or part number in each shop as well as using the general product/category query; equivalent models may have separate shop offers even when a generic query misses them. Count each shop’s relevant results and inspect its remaining pages before concluding that no other qualifying offer exists.
+For cheapest, tied, or complete-result tasks, keep a per-shop ledger of candidate names, prices, evidence for every requested attribute, and exact offer URLs. Treat search hits as candidates, not confirmed matches: inspect titles and product descriptions for each constraint, including meaningful model modifiers and specified attributes, and exclude related products or variants that do not meet them (for example, EVO vs. non-EVO or a different capacity or speed). Related products can be leads to investigate, but are not confirmed search results or a reason to stop searching. For capability requirements, accept equivalent terminology when the description or model specifications establish the requested capability; do not require an exact keyword match. Search both general product/category terms and distinctive model names or part numbers in every shop; when wording may vary, try a useful synonym or category route. Record each result count, inspect all relevant pages, and verify that no qualifying offer or equal-price tie was missed before choosing the winner.
 
 ## Bound the Search Before Closeout
 
 Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.
+
+## Reserve Budget for Completion
+
+Before a multi-shop purchase, plan for a separate cart review and checkout at every shop containing a selected offer; do not assume orders can be combined across shops. Reserve enough interactions to complete all requested orders, verify each order-received confirmation, and navigate to the solution page to submit the exact selected offer URLs. If the task asks only for results, still reserve time to submit them. Do not begin optional searches or checkout steps that leave a required order or final submission unfinished.
+
+## Final Offer-to-URL Check
+
+Before submission, verify each recorded offer against its own product page: confirm the retailer, product title, requested attributes, and exact current URL. Keep each URL paired with that verified offer, and do not infer a URL from a similar model or carry one forward after navigating to a different product.
```
