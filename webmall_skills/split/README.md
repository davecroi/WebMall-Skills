# Task split (train / val / test)

The one train/val/test split of the 91 WebMall tasks, shared by the runners
(`run_webmall_study.py`), SkillOpt training, the leakage guard and the held-out test
evaluation. The committed data is `split_v2/`; the original v1 split is not stored,
it is rebuilt in memory and verified by hash.

## How it was drawn

- Source: `Browsergym/browsergym/webmall/src/browsergym/webmall/task_sets.json`
  (11 task sets = categories, 91 tasks); its SHA-256 is stored in the manifest.
- Seed 42, one `random.Random` stream, task sets in file order. Within a category the
  task ids are naturally sorted (`Task2` before `Task10`), shuffled, then cut:
  1 train, 1 val, 3 test, the rest unused (v1: 11 / 11 / 33 / 36 unused).
- Drawn once before any experiment; never re-drawn.

## v1 to v2

split_v2 keeps every v1 assignment and only moves tasks out of "unused": per category
the next unused tasks, in the stored seed-42 order, go to val (+1) and then train (+2).
Test is unchanged. Reason (from the manifest): the pilot showed train F1 0.94 (few
failures to reflect on) and a noisy 11-task val gate. Categories with too few unused
tasks received less (see the table). `extends.manifest_sha256` is the SHA-256 of the v1
manifest (`339e0bea575d6e27640d5ffc94670a747a2fd334bd0f67d69d41dac11cb6e0f5`); a test
rebuilds v1 from seed 42 and checks the hash.

## Counts

| Split | Tasks |
|---|---|
| train | 26 |
| val | 21 |
| test | 33 |
| unused | 11 |

| Category (task set) | Train | Val | Test | Unused |
|---|---|---|---|---|
| Specific_Product (`WEBMALL_FIND_SPECIFIC_PRODUCT_V1`) | 3 | 2 | 3 | 4 |
| Cheapest_Product (`WEBMALL_FIND_CHEAPEST_OFFER_V1`) | 3 | 2 | 3 | 2 |
| Best_Fit_Specific (`WEBMALL_PRODUCTS_FULFILLING_SPECIFIC_REQUIREMENTS_V1`) | 3 | 2 | 3 | 3 |
| Best_Fit_Vague (`WEBMALL_PRODUCTS_SATISFYING_VAGUE_REQUIREMENTS_V1`) | 3 | 2 | 3 | 0 |
| Cheapest_Best_Fit_Specific (`WEBMALL_CHEAPEST_OFFER_SPECIFIC_REQUIREMENTS_V1`) | 3 | 2 | 3 | 2 |
| Cheapest_Best_Fit_Vague (`WEBMALL_CHEAPEST_OFFER_VAGUE_REQUIREMENTS_V1`) | 1 | 2 | 3 | 0 |
| Add_To_Cart (`WEBMALL_ADD_TO_CART_V1`) | 2 | 2 | 3 | 0 |
| Compatible_Products (`WEBMALL_FIND_COMPATIBLE_PRODUCTS_V1`) | 1 | 1 | 3 | 0 |
| Substitute (`WEBMALL_FIND_SUBSTITUTES_V1`) | 1 | 2 | 3 | 0 |
| Checkout (`WEBMALL_CHECKOUT_V1`) | 3 | 2 | 3 | 0 |
| FindAndOrder (`WEBMALL_END_TO_END_V1`) | 3 | 2 | 3 | 0 |

## Files

```
split_v2/
  split_manifest.json     # seed, source + source_sha256, extends{split, manifest_sha256,
                          # extra_per_category, reason}, per_category_counts, counts,
                          # per_category{<task_set_id>: {category, train, val, test,
                          # added{val, train}, unused}}, unused
  train/items.json        # [{"id", "category", "task_set_id"}, ...]
  val/items.json
  test/items.json
```

Python API: `make_split.load_items(split)`, `benchmarks.split_task_names(split)`
(`webmall.<id>` gym names). `make_split.py` also holds the builders (`build_split`,
`extend_split`, `build_split_v2`).

## Guarantees (enforced by `tests/`)

- The committed `split_v2/` equals the builder output (no hand edits).
- v1 rebuilt in memory from seed 42 hashes to `extends.manifest_sha256`.
- `source_sha256` equals the hash of the current `task_sets.json`, so editing the task
  file fails the tests instead of silently changing the held-out test set.
- v2 keeps v1 and test unchanged; train/val/test/unused are disjoint and cover all 91.
- The benchmarks contain exactly the split's tasks (test: 33, 50 steps, 1 repeat).

## Commands

```bash
Browsergym/.venv/bin/python -m webmall_skills.split.make_split          # refuses: split_v2 exists
Browsergym/.venv/bin/python -m webmall_skills.split.make_split --force --out /tmp/v2   # regenerate elsewhere, then diff -r
Browsergym/.venv/bin/python -m webmall_skills.split.make_split --v1 --out /tmp/v1      # v1 split (explicit --out required)
```

## Reproduce the thesis conditions

In `run_webmall_study.py` set `benchmark = "webmall_skills_test"` (registered by
`split_benchmarks.register()`), the agent `AGENT_GPT6_LUNA_AX_M`, and
`skill = None` (no skill), `"base"` or `"skillopt"`. `webmall_skills_val` and
`webmall_skills_train` select the other two splits.
