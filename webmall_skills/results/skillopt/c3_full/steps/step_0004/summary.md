# Step 4 (epoch 2) — rejected (gate)

Candidate v0004 vs. parent v0002: val F1 0.595 vs. 0.787; 3 edits applied from 1 failure / 1 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task2 | 1.000 | 1 | 24 |
| Webmall_Add_To_Cart_Task7 | 1.000 | 1 | 31 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task10 | 1.000 | 1 | 22 |
| Webmall_EndToEnd_Task6 | 1.000 | 1 | 33 |
| Webmall_Find_Cheapest_Offer_Task6 | 1.000 | 1 | 22 |
| Webmall_Find_Cheapest_Offer_Task8 | 1.000 | 1 | 18 |
| Webmall_Find_Compatible_Products_Task2 | 1.000 | 1 | 31 |
| Webmall_Find_Specific_Product_Task4 | 1.000 | 1 | 21 |
| Webmall_Find_Specific_Product_Task8 | 1.000 | 1 | 19 |
| Webmall_Find_Substitutes_Task6 | 1.000 | 1 | 22 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task8 | 0.632 | 0 | 47 |
| Webmall_Products_Satisfying_Vague_Requirements_Task3 | 0.500 | 0 | 42 |
| Webmall_Products_Satisfying_Vague_Requirements_Task5 | 0.667 | 0 | 18 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0004 | 21 | 0.595 | 0.571 | 0 | 0 |
| parent v0002 | 21 | 0.787 | 0.667 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0004 | 28.3 | 264,279 | 6,822 | 0.0298 | 157 | 3 |
| parent v0002 | 27.7 | 244,543 | 6,559 | 0.0277 | 159 | 1 |
| Δ candidate vs. parent | +0.6 (+2%) | +19,736 (+8%) | +263 (+4%) | +0.0021 (+8%) | -2 (-1%) | +2 |

Totals: candidate $0.63 / 3296 s (55 min); parent $0.58 / 3343 s (56 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.842 | -0.842 | 50 | 49 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 22 | 25 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 17 | 15 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 30 | 29 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 23 | 22 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 20 | 24 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.000 | 0.889 | -0.889 | 50 | 48 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 26 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 24 | 23 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 27 | 24 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 27 | 24 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 18 | 18 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 20 | 21 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.500 | 0.800 | -0.300 | 19 | 22 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.000 | 1.000 | -1.000 | 16 | 19 |
| Webmall_Find_Substitutes_Task3 | Substitute | 0.000 | 1.000 | -1.000 | 32 | 20 |
| Webmall_Checkout_Task8 | Checkout | 1.000 | 1.000 | +0.000 | 23 | 25 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 22 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 35 | 38 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 45 | 38 |

## Skill diff (parent → candidate)

```diff
--- v0002.md
+++ v0004.md
@@ -41,6 +41,8 @@
 If the task supplies a product-page URL, open it directly and verify the product title and relevant details. Use that page directly for requested cart or checkout actions; search across shops only when the task asks you to compare offers or find alternatives.
 3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
 4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
+
+Treat generation, tier, and other model-number differences as substantive, not formatting variations. A search redirect is only a candidate: confirm the product title and requested identifiers before recording its URL or price.
 5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
 6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.
 7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`.
@@ -58,3 +60,11 @@
 ## Bound the Search Before Closeout
 
 Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.
+
+## Final Cross-Retailer Duplicate Audit
+
+Before submitting an all-offers result, audit every confirmed qualifying model against every shop, even if that shop’s general category results appeared complete. Search the exact model name and useful model-number variants in each shop. Treat each retailer’s matching product page as a separate offer: record and submit each qualifying retailer-specific URL rather than reusing one shop’s URL or assuming identical models are a single offer. Reconcile the per-shop ledger against the final URL list before navigating to the solution page.
+
+## Verify the Exact Requested Specification
+
+For each candidate, confirm every requirement from evidence for that specific offer. Match the specification type the task asks for (such as base, boost, or maximum clock speed), units, and strict or inclusive threshold; do not substitute a related metric or infer a value from the model family. If the listing does not establish the required attribute, investigate the product description or exclude the candidate rather than treating an unverified assumption as confirmation.
```
