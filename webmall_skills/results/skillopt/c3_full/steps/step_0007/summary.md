# Step 7 (epoch 4) — accepted ★

Candidate v0007 vs. parent v0005: val F1 0.865 vs. 0.793; 2 edits applied from 2 failure / 1 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task7 | 1.000 | 1 | 22 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task6 | 0.000 | 0 | 44 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task3 | 0.667 | 0 | 25 |
| Webmall_Checkout_Task4 | 1.000 | 1 | 24 |
| Webmall_EndToEnd_Task8 | 0.667 | 0 | 50 |
| Webmall_Find_Cheapest_Offer_Task6 | 1.000 | 1 | 18 |
| Webmall_Find_Cheapest_Offer_Task8 | 1.000 | 1 | 20 |
| Webmall_Find_Specific_Product_Task4 | 1.000 | 1 | 19 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task4 | 0.167 | 0 | 36 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task8 | 0.267 | 0 | 43 |
| Webmall_Products_Satisfying_Vague_Requirements_Task3 | 1.000 | 1 | 31 |
| Webmall_Products_Satisfying_Vague_Requirements_Task5 | 1.000 | 1 | 25 |
| Webmall_Products_Satisfying_Vague_Requirements_Task6 | 1.000 | 1 | 28 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0007 | 21 | 0.865 | 0.810 | 0 | 0 |
| parent v0005 | 21 | 0.793 | 0.714 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0007 | 28.6 | 277,197 | 7,332 | 0.0314 | 156 | 1 |
| parent v0005 | 28.3 | 264,277 | 7,263 | 0.0301 | 154 | 1 |
| Δ candidate vs. parent | +0.3 (+1%) | +12,920 (+5%) | +69 (+1%) | +0.0013 (+4%) | +2 (+1%) | +0 |

Totals: candidate $0.66 / 3266 s (54 min); parent $0.63 / 3228 s (54 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 1.000 | 0.000 | +1.000 | 49 | 50 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 0.500 | +0.500 | 20 | 22 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 17 | 17 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 23 | 42 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 22 | 23 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 28 | 22 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 1.000 | 0.571 | +0.429 | 44 | 29 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.667 | 0.571 | +0.095 | 50 | 45 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 20 | 17 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 21 | 28 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 25 | 27 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 24 | 25 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 18 | 21 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 26 | 27 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.500 | 1.000 | -0.500 | 36 | 27 |
| Webmall_Find_Substitutes_Task4 | Substitute | 1.000 | 1.000 | +0.000 | 21 | 21 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 35 | 27 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 1.000 | +0.000 | 23 | 23 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 23 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 35 | 37 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 42 | 42 |

## Skill diff (parent → candidate)

```diff
--- v0005.md
+++ v0007.md
@@ -16,6 +16,8 @@
 - Add offers through result-list controls or product-page **Add to cart** controls. Use the product quantity field when needed.
 - Inspect `<shop>/cart/` for products and quantities; use **Proceed to Checkout** for checkout tasks.
 - At `<shop>/checkout/`, fill billing and card fields by label. Check default Country / Region and State / County against the task address; change mismatches using their inner search fields and matching options. Complete checkout with **Place order**, then verify that an order-received confirmation appears before proceeding to final submission.
+
+If requested items are in different shops, each shop has its own cart and checkout. Complete and verify an order for every shop containing a requested item; do not treat confirmation of one shop’s order as completion of the whole task. Navigate to the solution page and submit only after all required orders are confirmed.
 
 ## Task Categories
 
@@ -40,6 +42,8 @@
 
 If the task supplies a product-page URL, open it directly and verify the product title and relevant details. Use that page directly for requested cart or checkout actions; search across shops only when the task asks you to compare offers or find alternatives.
 3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
+
+For attribute-heavy searches, do not rely on one compound query containing every requirement. Search the product type or relevant category, then search distinctive brands, model families, and attribute terms separately; inspect results for equivalent wording and values that differ from the query. Use category listings as an additional discovery route when available. For cheapest-offer searches with noisy or broad results, inspect plausible candidates that could beat the current best, including remaining result pages as needed; do not consider a shop checked based only on the cheapest item encountered in a broad keyword search.
 4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
 5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
 6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.
```
