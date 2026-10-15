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
3. Shorten unsuccessful multiword queries to a keyword or synonym. On E-Store Athletes and CamelCases, avoid full titles containing typographic characters; use distinctive keywords instead.
4. Validate search hits: matching can occur in descriptions and inside longer words, not just titles.
5. Read titles and their following amounts from results lists. Normalize decimal and thousands separators before comparing across shops.
6. For cheapest searches, use ascending price sorting on E-Store Athletes, CamelCases, and Hardware Cafe. Compare TechTalk results yourself; its sorting controls do not offer price sorting.
7. Copy submission URLs exactly from product pages; their paths follow `/product/<slug>/`.

## Common Mistakes to Avoid

- Do not treat “Related products” on a redirected product page as search results.
- Do not interpret “No products were found matching your selection.” as proof of absence; rephrase the query.
- Do not wait for a stock-status label: observed product pages lack one.

---TRACE---
Overview: SOURCES §2
Output-format: SOURCES §3
Environment/1: SOURCES §1
Environment/2: SOURCES §1
Environment/3: F02
Environment/4: F01
Environment/5: F09
Environment/6: F10; F11; SOURCES §3
Environment/7: F18
Environment/8: F19
Environment/9: F20
Environment/10: F21
Category/1: SOURCES §2
Category/2: SOURCES §2
Category/3: SOURCES §2
Category/4: SOURCES §2
Category/5: SOURCES §2
Category/6: SOURCES §2
Category/7: SOURCES §2
Category/8: SOURCES §2
Category/9: SOURCES §2
Category/10: SOURCES §2
Category/11: SOURCES §2
Principle/1: SOURCES §3
Principle/2: F16; F23
Principle/3: F06; F07
Principle/4: F04; F05
Principle/5: F16; F14
Principle/6: F12
Principle/7: F13
Mistake/1: F09
Mistake/2: F08
Mistake/3: F17