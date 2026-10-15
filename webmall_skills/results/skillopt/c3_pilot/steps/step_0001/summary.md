# Step 1 (epoch 1) — rejected (gate)

Candidate v0001 vs. parent v0000: val F1 0.709 vs. 0.755; 3 edits applied from 1 failure / 2 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task2 | 1.000 | 1 | 21 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task4 | 1.000 | 1 | 20 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task3 | 0.667 | 0 | 23 |
| Webmall_Checkout_Task1 | 1.000 | 1 | 23 |
| Webmall_EndToEnd_Task8 | 0.667 | 0 | 50 |
| Webmall_Find_Cheapest_Offer_Task6 | 1.000 | 1 | 20 |
| Webmall_Find_Compatible_Products_Task2 | 1.000 | 1 | 25 |
| Webmall_Find_Specific_Product_Task8 | 1.000 | 1 | 23 |
| Webmall_Find_Substitutes_Task6 | 1.000 | 1 | 22 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task6 | 1.000 | 1 | 16 |
| Webmall_Products_Satisfying_Vague_Requirements_Task5 | 1.000 | 1 | 24 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0001 | 22 | 0.709 | 0.636 | 0 | 0 |
| parent v0000 | 22 | 0.755 | 0.682 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0001 | 30.4 | 294,794 | 7,956 | 0.0335 | 166 | 4 |
| parent v0000 | 28.0 | 261,517 | 7,454 | 0.0299 | 167 | 3 |
| Δ candidate vs. parent | +2.4 (+9%) | +33,277 (+13%) | +502 (+7%) | +0.0036 (+12%) | -1 (-1%) | +1 |

Totals: candidate $0.74 / 3653 s (61 min); parent $0.66 / 3683 s (61 min).

## Per task

Δ = candidate − parent. Runs: `selection_eval/<TaskId>`.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 17 | 15.5 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 22 | 22 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.000 | 0.500 | -0.500 | 50 | 48 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 0.500 | 1.000 | -0.500 | 20 | 20.5 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 31 | 28 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 19 | 20 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.800 | +0.000 | 40.5 | 23.5 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.500 | 0.500 | +0.000 | 25 | 19.5 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 0.500 | +0.500 | 23 | 24.5 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 36.5 | 36 |

## Skill diff (parent → candidate)

```diff
--- v0000.md
+++ v0001.md
@@ -41,10 +41,18 @@
 4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
 5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
 6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.
-7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`.
+
+- After checking all shops and remaining result pages, return every qualifying offer tied at the lowest price; do not stop at the first lowest-priced result.
+7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`. Treat matching products on different shop domains as separate offers, even when their product slugs are identical; include each shop's exact URL.
 
 ## Common Mistakes to Avoid
 
 - Do not treat “Related products” on a redirected product page as search results.
 - Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
 - Do not wait for a stock-status label: observed product pages lack one.
+
+## Completeness Checks
+
+- For attribute-based or vague searches, do not rely on one exact query. Search the product category and use relevant attribute synonyms, model terms, or specification values; validate candidate products using their titles and descriptions. Search results may include noisy matches or omit products whose wording differs from the query.
+- Before declaring a cheapest offer, reconcile the result count and relevant pages for each shop and compare every plausible qualifying candidate found. A low-priced candidate is not necessarily the lowest qualifying offer.
+- For tasks requesting multiple products, track each requested product separately through offer selection, cart addition, and checkout. Do not navigate to the solution page until every requested purchase is complete; then verify that the final submission includes every required offer URL.
```
