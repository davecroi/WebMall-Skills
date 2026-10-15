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

For cheapest-offer tasks, retain every distinct qualifying offer tied at the lowest price across all shops, including multiple matching products from the same shop. Capture and submit the exact URL for each tied offer.

For cheapest-offer, substitute, and end-to-end comparisons, also keep a per-shop ledger of matching candidates, prices, and exact URLs. Update the current best as you compare shops, and purchase only after the planned shop checks are complete.

For tasks asking for all qualifying offers or every offer tied at a maximum, keep a per-shop ledger of candidates, specifications, and exact offer URLs. After identifying a plausible product, search its distinctive model name or part number in each shop as well as using the general product/category query; equivalent models may have separate shop offers even when a generic query misses them. Count each shop’s relevant results and inspect its remaining pages before concluding that no other qualifying offer exists.

## Bound the Search Before Closeout

Plan a focused search pass for each shop and avoid repeating queries or navigation that produced no new evidence. Once every shop has been checked and the relevant result pages or categories have been covered, switch to recording exact URLs and submitting the result; do not spend the remaining interaction budget on optional searches while leaving the required submission unfinished.

## Verify Each Required Attribute
Qualify each distinct offer only when its own title, specifications, or description provide evidence for every required attribute. Distinguish a product having a feature from merely supporting an accessory or add-on that provides it: a header, connector, or compatibility claim alone does not prove the feature is included. Do not infer a feature from a customizable display, a similar product, or another variant in the same product family; for example, an LCD alone does not establish GIF playback. If evidence is unclear, inspect that offer’s product details and keep it out of the final qualifying set unless the requirement is supported.

## Complete Multi-Shop Purchases

For an end-to-end task with selected offers from different shops, group the chosen items by shop. Add all selected items for one shop to that shop’s cart and complete its checkout; repeat for each other shop. Before navigating away from a shop, verify its order-received confirmation. Complete every required order before navigating to the solution page and submitting the exact selected offer URLs.
