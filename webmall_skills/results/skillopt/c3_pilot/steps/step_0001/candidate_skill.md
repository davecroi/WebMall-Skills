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
- At `<shop>/checkout/`, fill billing and card fields by label. Check default Country / Region and State / County against the task address; change mismatches using their inner search fields and matching options. Complete checkout with **Place order**.

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
3. Shorten unsuccessful multiword queries to a keyword or synonym. Do not paste full product titles: drop curly quotes, dashes, degree signs and similar characters, and search with a few distinctive keywords.
4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.

- After checking all shops and remaining result pages, return every qualifying offer tied at the lowest price; do not stop at the first lowest-priced result.
7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`. Treat matching products on different shop domains as separate offers, even when their product slugs are identical; include each shop's exact URL.

## Common Mistakes to Avoid

- Do not treat “Related products” on a redirected product page as search results.
- Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
- Do not wait for a stock-status label: observed product pages lack one.

## Completeness Checks

- For attribute-based or vague searches, do not rely on one exact query. Search the product category and use relevant attribute synonyms, model terms, or specification values; validate candidate products using their titles and descriptions. Search results may include noisy matches or omit products whose wording differs from the query.
- Before declaring a cheapest offer, reconcile the result count and relevant pages for each shop and compare every plausible qualifying candidate found. A low-priced candidate is not necessarily the lowest qualifying offer.
- For tasks requesting multiple products, track each requested product separately through offer selection, cart addition, and checkout. Do not navigate to the solution page until every requested purchase is complete; then verify that the final submission includes every required offer URL.
