# Step 2 (epoch 1) — accepted ★

Candidate v0002 vs. parent v0000: val F1 0.787 vs. 0.705; 4 edits applied from 1 failure / 2 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Cheapest_Offer_Specific_Requirements_Task4 | 1.000 | 1 | 20 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task3 | 0.667 | 0 | 25 |
| Webmall_Checkout_Task1 | 1.000 | 1 | 24 |
| Webmall_EndToEnd_Task4 | 1.000 | 1 | 42 |
| Webmall_Find_Cheapest_Offer_Task2 | 1.000 | 1 | 22 |
| Webmall_Find_Cheapest_Offer_Task8 | 1.000 | 1 | 24 |
| Webmall_Find_Specific_Product_Task12 | 1.000 | 1 | 27 |
| Webmall_Find_Specific_Product_Task4 | 1.000 | 1 | 17 |
| Webmall_Find_Substitutes_Task6 | 1.000 | 1 | 21 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task8 | 0.000 | 0 | 50 |
| Webmall_Products_Satisfying_Vague_Requirements_Task3 | 0.800 | 0 | 40 |
| Webmall_Products_Satisfying_Vague_Requirements_Task5 | 1.000 | 1 | 23 |
| Webmall_Products_Satisfying_Vague_Requirements_Task6 | 0.000 | 0 | 50 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0002 | 21 | 0.787 | 0.667 | 0 | 0 |
| parent v0000 | 21 | 0.705 | 0.667 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0002 | 27.7 | 244,543 | 6,559 | 0.0277 | 159 | 1 |
| parent v0000 | 30.0 | 271,073 | 7,717 | 0.0310 | 195 | 4 |
| Δ candidate vs. parent | -2.3 (-8%) | -26,530 (-10%) | -1,157 (-15%) | -0.0032 (-10%) | -35 (-18%) | -3 |

Totals: candidate $0.58 / 3343 s (56 min); parent $0.65 / 4086 s (68 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.842 | 0.000 | +0.842 | 49 | 50 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 25 | 24 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 15 | 15 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 29 | 50 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 22 | 21 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 30 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.889 | 0.000 | +0.889 | 48 | 50 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 26 | 19 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 23 | 19 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 0.000 | 1.000 | -1.000 | 24 | 32 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 24 | 25 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 18 | 20 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 21 | 34 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.800 | +0.000 | 22 | 19 |
| Webmall_Find_Substitutes_Task4 | Substitute | 1.000 | 1.000 | +0.000 | 19 | 21 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 20 | 29 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 0.000 | +1.000 | 25 | 26 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 22 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 38 | 36 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 38 | 38 |

## Skill diff (parent → candidate)

```diff
--- v0000.md
+++ v0002.md
@@ -15,7 +15,7 @@
 - Inspect requested attributes in titles, available short descriptions, and Description-tab text already present in the accessibility tree.
 - Add offers through result-list controls or product-page **Add to cart** controls. Use the product quantity field when needed.
 - Inspect `<shop>/cart/` for products and quantities; use **Proceed to Checkout** for checkout tasks.
-- At `<shop>/checkout/`, fill billing and card fields by label. Check default Country / Region and State / County against the task address; change mismatches using their inner search fields and matching options. Complete checkout with **Place order**.
+- At `<shop>/checkout/`, fill billing and card fields by label. Check default Country / Region and State / County against the task address; change mismatches using their inner search fields and matching options. Complete checkout with **Place order**, then verify that an order-received confirmation appears before proceeding to final submission.
 
 ## Task Categories
 
@@ -37,6 +37,8 @@
 
 1. Review the current page and interaction history before acting. Use accessibility-tree bids and interact only with visible elements.
 2. For cross-shop searches, search each shop separately; compare titles and specifications, allowing for case, punctuation, and quote differences.
+
+If the task supplies a product-page URL, open it directly and verify the product title and relevant details. Use that page directly for requested cart or checkout actions; search across shops only when the task asks you to compare offers or find alternatives.
 3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
 4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
 5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
@@ -48,3 +50,11 @@
 - Do not treat “Related products” on a redirected product page as search results.
 - Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
 - Do not wait for a stock-status label: observed product pages lack one.
+
+## Cross-Shop Coverage for Complete and Tied Results
+
+For tasks asking for all qualifying offers or every offer tied at a maximum, keep a per-shop ledger of candidates, specifications, and exact offer URLs. After identifying a plausible product, search its distinctive model name or part number in each shop as well as using the general product/category query; equivalent models may have separate shop offers even when a generic query misses them. Count each shop’s relevant results and inspect its remaining pages before concluding that no other qualifying offer exists.
+
+## Bound the Search Before Closeout
+
+Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.
```
