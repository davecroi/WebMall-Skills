# Construction notes

## Scope of the automated contamination check

`check_contamination.py doc FILE` detects: model tokens (tokens mixing letters and digits), 3-word phrases of task text (at least two non-stopwords) and expected-answer URL slugs. It does NOT detect single words or two-word product/brand names. For these there is a separate report mode, `check_contamination.py words FILE`, which lists every word of the document whose stem matches a blocklist word. It never affects the exit status of `doc` mode. Its output for the skill is in `skill_word_overlap.txt` and is meant for manual sign-off (the list consists of generic English words; no product or brand name is among them).

## Drafting-model parameter probe

On 2026-10-01 a probe call showed that `gpt-6.1-sol` rejects `temperature=0` ("Only the default (1) value is supported") and accepts `temperature=1` and `reasoning_effort="high"`. Therefore temperature is not sent. `draft_request.json` contains exactly the API request parameters. The draft request was sent on 2026-10-06 at 12:32:09 UTC (the `created` field of `draft_response.json` records the response time).

## General instruction block example URL

The example submission in the general instruction block contains a shop 3 URL for a USB 2.0 cable product slug (`spire-usb-2-0-type-a-cable-male-to-male-1-metre`). That URL is itself an expected answer of a benchmark task. It appears in every task's instruction (so every agent sees it) and was therefore part of `sources.md` section 1 given to the drafting model. It does not appear in `SKILL.md`: `grep -n -i spire skills/base/SKILL.md` returns no match (exit code 1).

## Provenance of `<memory>` in the output-format paragraph

The examples in SOURCES section 3 show only `<think>` and `<action>`. `<memory>` comes from the spec's skill structure and from the evaluated agent configuration (`FLAGS_AX_M.use_memory = True` in `run_webmall_study.py`).

## Environment versions

- `git -C WebMall/Browsergym rev-parse HEAD`: `1aaef63d737308144f13b32e37ab5dbc3688d070`
- `git -C WebMall/AgentLab rev-parse HEAD`: `42e3f67ecfb093bec9982b721810ac9bcb409b2a`
- WebMall upstream commit (repo-root README.md): `2697d35cdfcfedcf1ade89b7ad86722db8daa8a7` (copied 2026-10-01)
- `docker ps --format '{{.Image}} {{.Names}}' | grep -i webmall`:
  ```
  bitnami/wordpress:latest WebMall_wordpress_shop1
  bitnami/wordpress:latest WebMall_wordpress_shop2
  bitnami/wordpress:latest WebMall_wordpress_shop4
  bitnami/wordpress:latest WebMall_wordpress_shop3
  nginx:latest WebMall_frontend
  docker.elastic.co/elasticsearch/elasticsearch:8.10.2 WebMall_elasticsearch
  bitnami/mariadb:latest WebMall_mariadb_shop1
  bitnami/mariadb:latest WebMall_mariadb_shop3
  bitnami/mariadb:latest WebMall_mariadb_shop4
  bitnami/mariadb:latest WebMall_mariadb_shop2
  ```
  (Images are `latest` tags, so they are not pinned; this is the state at 2026-10-06, not necessarily at exploration time.)
- Exploration date: 2026-10-06 (mtime of `evidence/summary.json` and commit date of `evidence/`).

## Stem fix re-run

`_stem` was extended to normalise a trailing "e" after the s/es rule, so "microphone" and "microphones" share the stem "microphon". Re-run on 2026-10-06 of `Browsergym/.venv/bin/python -m skill_construction.check_contamination terms skills/base/construction/probe_terms.txt` (exit 0, all 10 terms pass; `probe_terms_check.txt` left unchanged as the record of the exploration-time check):

```
ok     webcam
ok     wall mount
ok     desk lamp
ok     power strip
ok     tripod
ok     speaker
ok     microphone
ok     printer
ok     router
ok     document holder
```

## Not included in this repo

These records were written in the thesis repo, where the paths were relative to its `WebMall/` folder: `skills/base/` there is `webmall_skills/skills/base/` here, `skill_construction.check_contamination` is now `webmall_skills.contamination` and `skill_construction.<step>` is `webmall_skills.skill_construction.<step>`.

Two files from the draft step are not copied here. Both are kept in the thesis repo:

- `draft_request.json`: the exact request of the single draft call. Its one user message is `draft_prompt.md` + `sources.md` + `findings.md` concatenated (with `===== SOURCES =====` and `===== FINDINGS =====` separators, see `build_request` in `webmall_skills/skill_construction/draft_skill.py`). Parameters: `model=gpt-6.1-sol`, `reasoning_effort=high`, `max_completion_tokens=32000`, no temperature.
- `draft_response.json`: the raw API response. Its message content is byte-identical to `draft_SKILL.md`. Usage: 6,255 prompt tokens / 3,247 completion tokens.

Re-running `python -m webmall_skills.skill_construction.draft_skill` writes both files again; they are ignored by `.gitignore` in this folder.
