# Base skill review checklist

Reviewer: David Croissant — Date: 2026-10-07

- [x] `check_contamination.py doc skills/base/SKILL.md`: 0 hits
- [x] Every rule traces to `sources.md` or a finding ID (trace in `draft_SKILL.md`)
- [x] No product names, prices or inventory
- [x] Word count: 667 (≤ 800) — Token count (o200k_base): 885 (after human edits; draft: 660 / 880)
- [x] No condition names or experiment details in the text
- [x] Output-format paragraph present (<think>, <memory>, exactly one <action>)
- Render check (Step 5): `## Skill Knowledge` and `# WebMall Shopping Skill` present; agent_name GenericAgent-gpt-4.1-2025-04-14-skill_base
- Word-overlap list for manual sign-off: construction/skill_word_overlap.txt (see NOTES.md)

Human edits to `webmall_skills/skills/base/SKILL.md` (in the thesis repo: diff since thesis repo commit `2f768c4`, which holds the raw draft):
- Principle 3: removed shop restriction ("On E-Store Athletes and CamelCases"); F07 evidence does not limit the effect to two shops (TechTalk not tested with typographic characters, Hardware Cafe probe invalid).

Reviewed and left unchanged (reviewer decision):
- Environment, checkout: "Complete checkout with Place order" is inferred from the button label (F21) and the category description; no order was placed during exploration.
- Environment, search: per-shop single-hit redirect claims rest on few probes (E-Store Athletes: one term; Hardware Cafe not observed).
- Principle 5: "their following amounts" does not say which of two amounts on sale items is current (sale prices only seen once, F15 one-off).

Word-overlap list re-generated after edits: 37 words, all generic (added: "similar").
