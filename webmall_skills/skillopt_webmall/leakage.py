"""Test-leakage guard for candidate skills.

The optimizer sees train trajectories including gold URLs. A candidate that mentions
test-task phrases, model tokens or answer slugs is rejected before validation.
Blocklist = test split only; train vocabulary is overfitting (the gate measures it),
not leakage.

The blocklist blocks test answers and product identities, not generic strategy language:
  - slugs: all test answer slugs (unchanged).
  - phrases: a 3-gram is kept only if at least two of its tokens are neither in
    check_contamination.STOPWORDS nor in GENERIC_WORDS (shopping/checkout vocabulary).
  - model_tokens: pure spec tokens (16gb, 4k, ddr4, usb3, 3rd, 2x, 1920x1080, v2, ...) are
    dropped; product-like tokens (5900x, rtx4060, i7) are kept. A trailing "x" counts as a
    spec only after at most two digits.
  - words: unchanged (check_document does not use them).
"""
from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

from webmall_skills.contamination import (
    STOPWORDS, Blocklist, build_blocklist, check_document, load_tasks,
)


GENERIC_WORDS = {
    "price", "prices", "lowest", "highest", "cheap", "cheaper", "cheapest", "offer", "offers",
    "share", "return", "respective", "shopping", "cart", "checkout", "credit", "card", "number",
    "cvv", "expiry", "date", "name", "email", "street", "house", "zip", "city", "state",
    "country", "address", "following", "information", "page", "pages", "url", "urls",
    "multiple", "total", "order", "pay", "via", "using", "complete", "process", "product",
    "products", "shop", "shops", "store", "stores", "find", "search", "all", "same", "each",
    "other", "compatible", "suitable", "specific", "requirements", "need", "needs", "want",
    "looking", "buy", "purchase", "quantity", "two", "three", "four", "one",
}

_SPEC_TOKEN = re.compile(
    r"^(\d+(gb|tb|mb|k|g|d|v|w|hz|mhz|ghz|mm|cm|m|p|rd|th|nd|st)"
    r"|\d{1,2}x|v\d+|ddr\d|usb\d|\d+x\d+)$"
)


def _is_spec_token(token: str) -> bool:
    return bool(_SPEC_TOKEN.match(token))


def _informative(gram: str) -> bool:
    return sum(w not in STOPWORDS and w not in GENERIC_WORDS for w in gram.split()) >= 2


def build_test_blocklist(split_dir: Path) -> Blocklist:
    path = Path(split_dir) / "test" / "items.json"
    test_ids = {it["id"] for it in json.loads(path.read_text(encoding="utf-8"))}
    tasks = [t for t in load_tasks() if t["id"] in test_ids]
    if len(tasks) != len(test_ids):
        raise ValueError(f"test split references unknown task ids in {path}")
    full = build_blocklist(
        [t["task_text"] for t in tasks],
        [s for t in tasks for s in t["answer_slugs"]],
    )
    return replace(
        full,
        phrases={g for g in full.phrases if _informative(g)},
        model_tokens={t for t in full.model_tokens if not _is_spec_token(t)},
    )


def leakage_hits(skill_text: str, blocklist: Blocklist) -> list[str]:
    return check_document(skill_text, blocklist)
