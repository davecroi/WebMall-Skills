# WebMall Shopping Skill

Use this skill to search, compare offers, and complete requested shopping workflows.

**Output format:** Include `<think>` and `<memory>` in every answer, plus exactly one `<action>...</action>` containing one executable action. Never answer in plain text without an `<action>`.

## Environment

- Use E-Store Athletes, TechTalk, CamelCases, and Hardware Cafe at the supplied URLs.
- Finish by navigating to the supplied solution page. Enter exact full offer URLs separated by `###`, other requested values, or `Done` when no result remains after completion. Always press **Submit Final Result**.
- Identify search fields by role and label: E-Store Athletes uses “Search for:”; TechTalk and CamelCases use “Search products...”; Hardware Cafe uses “Search”.
- Submit searches by pressing Enter in the search field; clicking the search button gives equivalent results.
- Check whether search opened `/product/` directly: single hits redirect there on E-Store Athletes and CamelCases; TechTalk retains a results list.
- Read result counts and follow pagination for remaining results. Page capacities are 9, 12, 16, and 16 respectively; scroll to make pagination links visible before interacting.
- Inspect requested attributes in titles, available short descriptions, and Description-tab text already present in the accessibility tree.
- Add offers through result-list controls or product-page **Add to cart** controls. Use the product quantity field when needed.
- Inspect `<shop>/cart/` for products and quantities; use **Proceed to Checkout** for checkout tasks.
- At `<shop>/checkout/`, fill billing and card fields by label. Check default Country / Region and State / County against the task address; change mismatches using their inner search fields and matching options. Complete checkout with **Place order**, then verify that an order-received confirmation appears before proceeding to final submission.

## Task Categories

| Category | Goal | Key steps |
|---|---|---|
| Find Specific Product | All named-product offers | Search all shops; collect matching offers. |
| Products Fulfilling Specific Requirements | All qualifying offers | Search all shops; verify specified attributes. |
| Products Satisfying Vague Requirements | Relevant offers | Interpret descriptions; search shops; assess suitability. |
| Find Substitutes | Cheaper alternatives | Find alternatives for unavailable or unsatisfactory items; compare cost. |
| Find Compatible Products | Compatible offers | Search shops; reason over compatibility with the given item. |
| Find Cheapest Offer | Cheapest named-product offer | Search all shops; compare matching offers. |
| Cheapest Offer Specific Requirements | Cheapest qualifying offer | Verify constraints across shops; compare qualifying offers. |
| Cheapest Offer Vague Requirements | Cheapest suitable offer | Interpret needs; assess suitability across shops; compare cost. |
| Add to Cart | Requested cart additions | Locate specified offers; add them to the cart. |
| Checkout | Completed checkout | Add the offer; provide requested shipping and billing details; complete checkout. |
| End To End | Cheapest-offer purchase | Search and compare across shops; add cheapest offer; complete checkout. |

## General Principles

1. Review the current page and interaction history before acting. Use accessibility-tree bids and interact only with visible elements.
2. For cross-shop searches, search each shop separately; compare titles and specifications, allowing for case, punctuation, and quote differences.

If the task supplies a product-page URL, open it directly and verify the product title and relevant details. Use that page directly for requested cart or checkout actions; search across shops only when the task asks you to compare offers or find alternatives.
3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.
7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`.

## Common Mistakes to Avoid

- Do not treat “Related products” on a redirected product page as search results.
- Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
- Do not wait for a stock-status label: observed product pages lack one.

## Cross-Shop Coverage for Complete and Tied Results

For cheapest, tied, or complete-result tasks, keep a per-shop ledger of candidate names, prices, evidence for every requested attribute, and exact offer URLs. Treat search hits as candidates, not confirmed matches: inspect titles and product descriptions for each constraint, including meaningful model modifiers and specified attributes, and exclude related products or variants that do not meet them (for example, EVO vs. non-EVO or a different capacity or speed). Related products can be leads to investigate, but are not confirmed search results or a reason to stop searching. For capability requirements, accept equivalent terminology when the description or model specifications establish the requested capability; do not require an exact keyword match. Search both general product/category terms and distinctive model names or part numbers in every shop; when wording may vary, try a useful synonym or category route. Record each result count, inspect all relevant pages, and verify that no qualifying offer or equal-price tie was missed before choosing the winner.

## Bound the Search Before Closeout

Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.

## Reserve Budget for Completion

Before a multi-shop purchase, plan for a separate cart review and checkout at every shop containing a selected offer; do not assume orders can be combined across shops. Reserve enough interactions to complete all requested orders, verify each order-received confirmation, and navigate to the solution page to submit the exact selected offer URLs. If the task asks only for results, still reserve time to submit them. Do not begin optional searches or checkout steps that leave a required order or final submission unfinished.

## Final Offer-to-URL Check

Before submission, verify each recorded offer against its own product page: confirm the retailer, product title, requested attributes, and exact current URL. Keep each URL paired with that verified offer, and do not infer a URL from a similar model or carry one forward after navigating to a different product.
