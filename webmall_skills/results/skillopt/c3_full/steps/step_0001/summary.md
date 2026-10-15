# Step 1 (epoch 1) — rejected (gate)

Candidate v0001 vs. parent v0000: val F1 0.610 vs. 0.705; 4 edits applied from 1 failure / 3 success patches.

## Train batch

| Task | F1 | CR | Steps |
|---|---|---|---|
| Webmall_Add_To_Cart_Task2 | 1.000 | 1 | 22 |
| Webmall_Add_To_Cart_Task7 | 1.000 | 1 | 26 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task10 | 1.000 | 1 | 23 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task6 | 0.000 | 0 | 21 |
| Webmall_Checkout_Task4 | 1.000 | 1 | 23 |
| Webmall_Checkout_Task5 | 1.000 | 1 | 23 |
| Webmall_EndToEnd_Task6 | 1.000 | 1 | 35 |
| Webmall_EndToEnd_Task8 | 0.000 | 0 | 50 |
| Webmall_Find_Cheapest_Offer_Task6 | 1.000 | 1 | 20 |
| Webmall_Find_Compatible_Products_Task2 | 1.000 | 1 | 20 |
| Webmall_Find_Specific_Product_Task8 | 1.000 | 1 | 25 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task4 | 0.625 | 0 | 42 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task6 | 1.000 | 1 | 26 |

## Val: candidate vs. parent

| Skill | Runs | Mean F1 | Mean CR | Env errors | Missing |
|---|---|---|---|---|---|
| candidate v0001 | 21 | 0.610 | 0.571 | 0 | 0 |
| parent v0000 | 21 | 0.705 | 0.667 | 0 | 0 |

## Efficiency

Mean per val run (successes and failures alike). Cost = tokens × config prices; time = agent (LLM) + browser seconds. Step-limit hits = runs that stopped at the step limit.

| Condition | Steps | Input tokens | Output tokens | Cost ($) | Time (s) | Step-limit hits |
|---|---|---|---|---|---|---|
| candidate v0001 | 30.0 | 286,188 | 7,805 | 0.0325 | 176 | 3 |
| parent v0000 | 30.0 | 271,073 | 7,717 | 0.0310 | 195 | 4 |
| Δ candidate vs. parent | -0.0 (-0%) | +15,115 (+6%) | +89 (+1%) | +0.0016 (+5%) | -19 (-10%) | -1 |

Totals: candidate $0.68 / 3687 s (61 min); parent $0.65 / 4086 s (68 min).

## Per task

Δ = candidate − parent.

| Task | Category | candidate F1 | parent F1 | Δ candidate − parent | candidate steps | parent steps |
|---|---|---|---|---|---|---|
| Webmall_Find_Specific_Product_Task6 | Specific_Product | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Find_Specific_Product_Task7 | Specific_Product | 1.000 | 1.000 | +0.000 | 17 | 24 |
| Webmall_Find_Cheapest_Offer_Task4 | Cheapest_Product | 1.000 | 1.000 | +0.000 | 21 | 15 |
| Webmall_Find_Cheapest_Offer_Task7 | Cheapest_Product | 0.000 | 0.000 | +0.000 | 26 | 50 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task2 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 25 | 21 |
| Webmall_Products_Fulfilling_Specific_Requirements_Task5 | Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 36 | 30 |
| Webmall_Products_Satisfying_Vague_Requirements_Task4 | Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Products_Satisfying_Vague_Requirements_Task2 | Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 50 | 50 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task9 | Cheapest_Best_Fit_Specific | 0.000 | 1.000 | -1.000 | 21 | 19 |
| Webmall_Cheapest_Offer_Specific_Requirements_Task3 | Cheapest_Best_Fit_Specific | 1.000 | 1.000 | +0.000 | 29 | 19 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task2 | Cheapest_Best_Fit_Vague | 1.000 | 1.000 | +0.000 | 22 | 32 |
| Webmall_Cheapest_Offer_Vague_Requirements_Task5 | Cheapest_Best_Fit_Vague | 0.000 | 0.000 | +0.000 | 27 | 25 |
| Webmall_Add_To_Cart_Task1 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 18 | 20 |
| Webmall_Add_To_Cart_Task6 | Add_To_Cart | 1.000 | 1.000 | +0.000 | 39 | 34 |
| Webmall_Find_Compatible_Products_Task4 | Compatible_Products | 0.800 | 0.800 | +0.000 | 34 | 19 |
| Webmall_Find_Substitutes_Task4 | Substitute | 0.000 | 1.000 | -1.000 | 16 | 21 |
| Webmall_Find_Substitutes_Task3 | Substitute | 1.000 | 1.000 | +0.000 | 28 | 29 |
| Webmall_Checkout_Task8 | Checkout | 0.000 | 0.000 | +0.000 | 23 | 26 |
| Webmall_Checkout_Task6 | Checkout | 1.000 | 1.000 | +0.000 | 22 | 22 |
| Webmall_EndToEnd_Task5 | FindAndOrder | 1.000 | 1.000 | +0.000 | 37 | 36 |
| Webmall_EndToEnd_Task3 | FindAndOrder | 1.000 | 1.000 | +0.000 | 38 | 38 |

## Skill diff (parent → candidate)

```diff
--- v0000.md
+++ v0001.md
@@ -36,7 +36,11 @@
 ## General Principles
 
 1. Review the current page and interaction history before acting. Use accessibility-tree bids and interact only with visible elements.
+
+After consequential actions, inspect the resulting URL, page content, or confirmation status to verify they succeeded. If an action times out or errors, re-check the current page and state before retrying: it may already have succeeded, and repeating it could cause duplicate actions.
 2. For cross-shop searches, search each shop separately; compare titles and specifications, allowing for case, punctuation, and quote differences.
+
+For multi-part requirements, normalize equivalent configuration notation (such as total kit capacity versus per-module capacity) and verify every required attribute. Reject near-matches that differ in a required configuration, socket, or specification.
 3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
 4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
 5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
@@ -48,3 +52,11 @@
 - Do not treat “Related products” on a redirected product page as search results.
 - Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
 - Do not wait for a stock-status label: observed product pages lack one.
+
+## Search and Verification Checklist
+
+Do not treat a keyword-search result as a complete product list or as proof that a product qualifies. Track the result count, inspect all relevant pages, and search useful model-name, category, and feature synonyms when results appear incomplete. Open plausible candidates and verify both product type and each requested attribute from the product details. For cheapest tasks, compare qualifying candidates across every shop and continue checking results and ties before choosing; for “all offers” tasks, inspect all plausible variants rather than only the first matching model.
+
+## Task Closeout
+
+Before finishing, check the task’s required outcomes: all requested products are selected, every required cart and checkout is completed (including separate shops when needed), and all required offer URLs are recorded exactly. Then navigate to the solution page, enter the required URL list or `Done`, and press **Submit Final Result**. Do not end after browsing, filling checkout fields, or entering a submission without submitting it.
```
