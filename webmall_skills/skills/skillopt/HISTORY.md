# C3 skill lineage (SkillOpt on WebMall)

Val F1 = mean per-task F1 over 21 val tasks × 1 repeat (the gate score); val CR = mean task completion. ★ = became the new best skill; the last ★ is `SKILL.md`.

| Version | Epoch | Parent | Edits | Val F1 before → after | Val CR | Decision | Best |
|---|---|---|---|---|---|---|---|
| v0000 |  | — | base skill | — → 0.705 | 0.667 | seed | ★ |
| v0001 | 1 | v0000 | append: ## Search and Verification Checklist Do not treat a keyword-…; insert_after: After consequential actions, inspect the resulting URL, page…; append: ## Task Closeout Before finishing, check the task’s required…; insert_after: For multi-part requirements, normalize equivalent configurat… | 0.705 → 0.610 | 0.571 | rejected (gate) |  |
| v0002 | 1 | v0000 | append: ## Cross-Shop Coverage for Complete and Tied Results For tas…; append: ## Bound the Search Before Closeout Plan a focused search pa…; replace: - At `<shop>/checkout/`, fill billing and card fields by lab…; insert_after: If the task supplies a product-page URL, open it directly an… | 0.705 → 0.787 | 0.667 | accepted | ★ |
| v0003 | 2 | v0002 | replace: For cheapest, tied, or complete-result tasks, keep a per-sho…; insert_after: ## Reserve Budget for Completion Before a multi-shop purchas…; append: ## Final Offer-to-URL Check Before submission, verify each r… | 0.787 → 0.638 | 0.571 | rejected (gate) |  |
| v0004 | 2 | v0002 | append: ## Final Cross-Retailer Duplicate Audit Before submitting an…; append: ## Verify the Exact Requested Specification For each candida…; insert_after: Treat generation, tier, and other model-number differences a… | 0.787 → 0.595 | 0.571 | rejected (gate) |  |
| v0005 | 3 | v0002 | insert_after: For cheapest-offer, substitute, and end-to-end comparisons, …; append: ## Verify Each Required Attribute Qualify each distinct offe…; insert_after: For cheapest-offer tasks, retain every distinct qualifying o… | 0.787 → 0.793 | 0.714 | accepted | ★ |
| v0006 | 3 | v0005 | replace: Qualify each distinct offer only when its own title, specifi…; append: ## Complete Multi-Shop Purchases For an end-to-end task with… | 0.793 → 0.667 | 0.667 | rejected (gate) |  |
| v0007 | 4 | v0005 | insert_after: For attribute-heavy searches, do not rely on one compound qu…; insert_after: If requested items are in different shops, each shop has its… | 0.793 → 0.865 | 0.810 | accepted | ★ |
| v0008 | 4 | v0007 | insert_after: For cheapest-offer searches, when ascending price order is c… | 0.865 → 0.837 | 0.714 | rejected (gate) |  |

## WebMall aggregate metrics of accepted versions (val)

| Version | CR | P | R | F1 | Env errors |
|---|---|---|---|---|---|
| v0000 | 0.667 | 0.714 | 0.698 | 0.706 | 0 |
| v0002 | 0.667 | 0.804 | 0.775 | 0.790 | 0 |
| v0005 | 0.714 | 0.798 | 0.795 | 0.797 | 0 |
| v0007 | 0.810 | 0.883 | 0.867 | 0.875 | 0 |

Cost: $9.86 total (target $9.43, optimizer $0.43), 316 rollouts; ledger shared by pilot and full run.
