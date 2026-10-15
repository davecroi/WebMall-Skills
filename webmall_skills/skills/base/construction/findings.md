# Shop exploration findings

Produced from `evidence/` (see `summary.json`). Behaviour only; no catalogue content.
A finding is a **rule** if it held in ≥ 2 probes, otherwise **one-off**.

Shops: shop1 = E-Store Athletes, shop2 = TechTalk, shop3 = CamelCases, shop4 = Hardware Cafe.
Invalid probes ignored below: shop1 webcam/button and shop1 tripod/button (click timeout in the
exploration script), and shop4 long/short query (the script searched the shop's own name instead of a
product title).

## F01 — Pressing Enter in the search field and clicking the search button give the same result
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: all 10 probe terms, enter vs. button (38 valid pairs); every pair ended on the same URL with the same number of result links
- Evidence: evidence/shop2__search_enter__router.txt, evidence/shop2__search_button__router.txt, evidence/shop4__search_enter__printer.txt, evidence/shop4__search_button__printer.txt
- Why it matters: type the query into the search field and press Enter; there is no need to find the search button.

## F02 — The search field and its button are labelled differently in each shop
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: home page and every search page
- Evidence: evidence/shop1__home.txt, evidence/shop2__home.txt, evidence/shop3__home.txt, evidence/shop4__home.txt
- Why it matters: look for the field by role, not by a fixed label. shop1 has a searchbox 'Search for:' with a button 'Search'; shop2 has a textbox 'Search products...' with an unlabelled button (plus a separate 'search form toggle' button); shop3 has a textbox 'Search products...' next to a category select ('All Categories') and an unlabelled button; shop4 has a searchbox 'Search' with a button 'Search Now' and a separate category select ('Select a category').

## F03 — Search can be run directly by URL
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: all search probes; the URL patterns were read from the result page URLs (inferred: opening such a URL directly was not tested separately)
- Evidence: evidence/shop1__search_enter__speaker.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop3__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: you can skip the form and open the results page directly. shop1 and shop4 use `<shop>/?s=<query>&post_type=product`; shop2 and shop3 use `<shop>/?post_type=product&s=<query>&product_cat=`; words in the query are joined with `+`.

## F04 — Search matches terms in the description too, not only in the title
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: webcam, wall mount, power strip, printer, router, tripod, microphone
- Evidence: evidence/shop1__search_enter__printer.txt, evidence/shop3__search_enter__wall-mount.txt, evidence/shop4__search_enter__webcam.txt, evidence/shop2__search_enter__wall-mount.txt
- Why it matters: many results do not contain the query word in their title at all; check every hit's title and details instead of assuming every result is the kind of product you asked for.

## F05 — Search matches parts of words (substrings)
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: desk lamp (the query word 'lamp' matched a longer word that contains it, in the description of an unrelated product), speaker (also matches the plural form in titles)
- Evidence: evidence/shop1__search_enter__desk-lamp.txt, evidence/shop3__search_enter__desk-lamp.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: singular vs. plural rarely matters, but short query words can produce surprising matches inside other words, so check whether a hit really fits.

## F06 — A query with several words only returns products that contain every word
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: desk lamp, document holder; both two-word probes returned 0 or 1 results on every shop, and the single hits did not contain the phrase (inferred: all words required; one-word vs. two-word queries were not compared directly)
- Evidence: evidence/shop2__search_enter__desk-lamp.txt, evidence/shop4__search_enter__desk-lamp.txt, evidence/shop1__search_enter__document-holder.txt, evidence/shop3__search_enter__document-holder.txt
- Why it matters: each extra word narrows the search; if a two-word query returns nothing, retry with one key word or a synonym before deciding a shop does not have the item.

## F07 — Full product titles with typographic characters found nothing; their first two words did
- Status: rule
- Shops: shop1, shop3 (shop2 behaved differently, see below; shop4 probe invalid)
- Probes: long query (full product title) vs. short query (first two words of the title)
- Evidence: evidence/shop1__long_query.txt, evidence/shop1__short_query.txt, evidence/shop3__long_query.txt, evidence/shop3__short_query.txt, evidence/shop2__long_query.txt, evidence/shop1__cart.txt, evidence/shop3__cart.txt
- Why it matters: do not paste a full product title into the search. On shop1 and shop3 the full title found nothing, while its first two words found the product (shop1: a page of results; shop3: straight to the product page). Both failing titles contained typographic characters (curly quotes, a degree sign, an en dash), which the shops store as HTML entities (e.g. `&#8221;`, `&#8211;` in the cart), so the typed character may not match the stored text. The one long query without such characters (shop2) found the product. Length and typographic characters are therefore confounded: the cause could be either. Drop curly quotes, dashes, degree signs and similar characters, and shorten the query to a few distinctive key words.

## F08 — The no-results message is the same in every shop
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: nonsense query, document holder, long query (shop1, shop3)
- Evidence: evidence/shop1__no_results.txt, evidence/shop2__no_results.txt, evidence/shop3__no_results.txt, evidence/shop4__no_results.txt
- Why it matters: the text 'No products were found matching your selection.' means the query matched nothing; rephrase the query (see F06, F07) instead of concluding the product does not exist.

## F09 — A search with exactly one hit opens the product page directly on shop1 and shop3, but not on shop2
- Status: rule
- Shops: shop1, shop2, shop3
- Probes: single-hit searches: desk lamp, short query, long query
- Evidence: evidence/shop1__search_enter__desk-lamp.txt, evidence/shop3__search_enter__desk-lamp.txt, evidence/shop3__short_query.txt, evidence/shop2__short_query.txt
- Why it matters: after a search, check whether you are on a results list or already on a product page (URL contains `/product/`). On shop1 and shop3 a single hit takes you to its product page, and the products listed there are 'Related products', not search results; on shop2 a single hit is shown as a list with 'Showing the single result'.

## F10 — The result count is shown above the list, and the page size differs per shop
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: webcam, speaker, microphone, router, tripod, power strip
- Evidence: evidence/shop1__search_enter__microphone.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop3__search_enter__webcam.txt, evidence/shop4__search_enter__router.txt
- Why it matters: read 'Showing 1–<n> of <total> results' (or 'Showing all <n> results' / 'Showing the single result') to know whether more pages exist. One page holds 9 results on shop1, 12 on shop2, and 16 on shop3 and shop4.

## F11 — Results continue on further pages behind page-number links
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: speaker, microphone, webcam (any query with more results than one page)
- Evidence: evidence/shop1__search_enter__speaker.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop3__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: when the total is larger than the page size, the remaining results are only reachable through links 'Page 2', 'Page 3', … below the list (shop1–shop3 end with a '→' next-page link, shop4 with a 'Next Page' link; long ranges are shortened with '…'). These links sit below the visible area but are already in the AX tree.

## F12 — Sorting options differ: shop2 offers no price sort control
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: all search result pages with results
- Evidence: evidence/shop1__search_enter__webcam.txt, evidence/shop3__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt, evidence/shop2__search_enter__speaker.txt
- Why it matters: on shop1, shop3 and shop4 the select 'Shop order' (default 'Relevance') offers 'Sort by price: low to high' and 'high to low', which helps find the cheapest offer. shop2 results are 'Sorted by popularity' and its sidebar 'Sort By' select only offers 'Default' and 'Popularity', so there you have to compare prices yourself (sorting through URL parameters was not tested); shop2 instead has a 'Price Range' filter with two number fields in the sidebar.

## F13 — Product pages follow `/product/<slug>/` in every shop
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: product page scenario, single-hit redirects
- Evidence: evidence/shop1__product_page.txt, evidence/shop2__product_page.txt, evidence/shop3__product_page.txt, evidence/shop4__product_page.txt
- Why it matters: the answer URL is `<shop base URL>/product/<slug>/`; copy it exactly from the product page URL, as the slug is long and derived from the full title.

## F14 — Price formats differ between shops
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: all result pages, product pages, cart
- Evidence: evidence/shop1__product_page.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop3__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: convert prices to one format before comparing across shops. shop1, shop3 and shop4 show '<amount> €' with a comma as decimal separator and a dot as thousands separator; shop2 shows '€<amount>' with a dot as decimal separator and no thousands separator. shop1 puts the label 'Selling On:' before the price.

## F15 — A sale shows both the old and the new price (seen on shop2)
- Status: one-off
- Shops: shop2
- Probes: home page
- Evidence: evidence/shop2__home.txt
- Why it matters: a discounted product is marked 'PRODUCT ON SALE' and shows 'Original price was: €<amount>.' followed by 'Current price is: €<amount>.'; the current price is the one that counts. shop2 also has a 'Sale' link in its header menu.

## F16 — In result lists, the price follows the title of each product
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: all result pages with results
- Evidence: evidence/shop1__search_enter__webcam.txt, evidence/shop2__search_enter__speaker.txt, evidence/shop3__search_enter__speaker.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: you can read titles and prices straight from the results list, without opening each product. Each entry has a heading with the title, then the price as text. On shop1 the result heading is in Title Case and the link text repeats the title in its original case and in Title Case, followed by 'Selling On:<price>', so compare titles case-insensitively; on shop2 and shop3 the link text ends with the price; on shop4 it is the title only.

## F17 — Product pages show no stock status
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: product page scenario
- Evidence: evidence/shop1__product_page.txt, evidence/shop2__product_page.txt, evidence/shop3__product_page.txt, evidence/shop4__product_page.txt
- Why it matters: no product page showed 'In stock' or 'Out of stock' text; an 'Add to cart' button and a 'Product quantity' field were shown each time, so do not wait for a stock label.

## F18 — Specifications are in the title, the short description and the 'Description' tab
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: product page scenario, single-hit product pages
- Evidence: evidence/shop1__product_page.txt, evidence/shop2__product_page.txt, evidence/shop3__product_page.txt, evidence/shop4__product_page.txt
- Why it matters: check the attributes a task asks for in three places: the long title, the short description paragraph next to the price (shop2, shop3, shop4), and the 'Description' tab, whose text is already in the AX tree without clicking. There is no 'Additional information' tab; shop1 and shop3 also have a 'Reviews (<n>)' tab. A 'Category:' link sits above the tabs on all shops.

## F19 — Add-to-cart controls on product pages and in result lists
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: product page scenario, all result pages
- Evidence: evidence/shop1__product_page.txt, evidence/shop4__product_page.txt, evidence/shop2__search_enter__router.txt, evidence/shop4__search_enter__router.txt
- Why it matters: product pages have a 'Product quantity' field and a button 'Add to cart' (shop4: 'ADD TO CART'; shop1 also has 'Buy now'). Result lists also offer 'Add to cart: “<title>”' per product (a link on shop1–shop3, a button on shop4), so a product can be added without opening it.

## F20 — The cart page lists products in a table and links to checkout
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: cart after add-to-cart
- Evidence: evidence/shop1__cart.txt, evidence/shop2__cart.txt, evidence/shop3__cart.txt, evidence/shop4__cart.txt
- Why it matters: the cart is at `<shop>/cart/` and shows a table 'Products in cart' (columns 'PRODUCT', 'TOTAL') with a quantity field, 'Reduce' / 'Increase quantity' buttons and a 'Remove <title>' button per row, an 'Add a coupon' button, 'Subtotal' / 'Total', and the link 'Proceed to Checkout'.

## F21 — The checkout form has the same fields on all shops, but in a slightly different order
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: checkout scenario
- Evidence: evidence/shop1__checkout.txt, evidence/shop2__checkout.txt, evidence/shop3__checkout.txt, evidence/shop4__checkout.txt
- Why it matters: the checkout is at `<shop>/checkout/`. Under 'Billing details' it has the required textboxes 'First name', 'Last name', 'Street address', 'Town / City', 'Postcode / ZIP', 'Email address', the optional 'Apartment, suite, unit, etc. (optional)' and 'Phone (optional)', and the selects 'Country / Region' (marked required) and 'State / County'. Both are comboboxes already filled in by default, each with an inner search textbox; check them against the address in the task and, if they differ, change them by typing into the combobox's inner textbox and picking the matching option. shop1 and shop2 put 'Town / City' before 'Postcode / ZIP', shop3 and shop4 the other way round, so fill fields by label, not by position. Below are 'Order notes (optional)', the card fields 'Cardholder Name *', 'Card Number *', 'Expiry (MM/YY) *', 'CVC *', and the button 'Place order' (shop4: 'PLACE ORDER'). There is also an 'Enter your coupon code' button, and there are no checkboxes or radio buttons.

## F22 — The solution page has one text field and one submit button
- Status: one-off
- Shops: none (separate solution page)
- Probes: solution page scenario
- Evidence: evidence/solution__page.txt
- Why it matters: the page titled 'WebMall - Submit Final Result' has a single textbox 'Type your final answer here...' and a button 'Submit Final Result'; there are no other inputs.

## F23 — The same offer can appear in several shops at different prices and behind different search terms
- Status: rule
- Shops: shop1, shop2, shop3, shop4
- Probes: result titles compared across shops (webcam, desk lamp, speaker, wall mount)
- Evidence: evidence/shop1__search_enter__webcam.txt, evidence/shop2__search_enter__webcam.txt, evidence/shop3__search_enter__wall-mount.txt, evidence/shop4__search_enter__speaker.txt
- Why it matters: titles that match after ignoring punctuation and quote characters appeared in two shops at once, usually at different prices, and the same offer sometimes showed up for different probe terms in different shops; search every shop separately and compare offers by title and specifications.
