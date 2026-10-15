import json
import re

import pytest

from webmall_skills.contamination import build_blocklist, load_tasks
from webmall_skills.paths import SKILLS_DIR
from webmall_skills.skillopt_webmall.leakage import build_test_blocklist, leakage_hits
from webmall_skills.split.make_split import SPLIT_V2_DIR


def test_blocklist_only_covers_test_tasks():
    bl = build_test_blocklist(SPLIT_V2_DIR)
    test_ids = {it["id"] for it in json.loads((SPLIT_V2_DIR / "test" / "items.json").read_text())}
    tasks = [t for t in load_tasks() if t["id"] in test_ids]
    expected = build_blocklist([t["task_text"] for t in tasks],
                               [s for t in tasks for s in t["answer_slugs"]])
    assert bl.slugs == expected.slugs
    assert bl.words == expected.words
    assert bl.phrases <= expected.phrases and bl.model_tokens <= expected.model_tokens


def test_base_skill_has_no_hits():
    base = (SKILLS_DIR / "base/SKILL.md").read_text()
    assert leakage_hits(base, build_test_blocklist(SPLIT_V2_DIR)) == []


def test_test_answer_slug_is_a_hit():
    bl = build_test_blocklist(SPLIT_V2_DIR)
    slug = sorted(bl.slugs)[0]
    hits = leakage_hits(f"Prefer /product/{slug}/ when in doubt.", bl)
    assert any(slug in h for h in hits)


def test_generic_text_passes():
    bl = build_test_blocklist(SPLIT_V2_DIR)
    assert leakage_hits("Scroll down to see pagination links before clicking.", bl) == []


GENERIC_SENTENCES = [
    "Always pick the lowest price across all four shops.",
    "If multiple offers share the same price, return all of them.",
    "Add the product to the respective shopping cart before checkout.",
    "Check the 3rd page of results.",
    "Fill in the credit card number, CVV and expiry date from the task.",
    "Compare 16GB and 32GB variants; 4K and DDR4 are attributes.",
]


@pytest.mark.parametrize("sentence", GENERIC_SENTENCES)
def test_generic_strategy_language_is_not_blocked(sentence):
    assert leakage_hits(sentence, build_test_blocklist(SPLIT_V2_DIR)) == []


def test_answer_slug_still_blocked():
    bl = build_test_blocklist(SPLIT_V2_DIR)
    assert leakage_hits(f"see /product/{sorted(bl.slugs)[0]}/", bl)


def test_product_like_model_tokens_still_blocked():
    bl = build_test_blocklist(SPLIT_V2_DIR)
    prods = sorted(t for t in bl.model_tokens
                   if re.search(r"[a-z]", t) and len(re.findall(r"\d", t)) >= 3)
    assert prods
    assert leakage_hits(f"Look for the {prods[0]} model.", bl)


def test_spec_token_filter():
    from webmall_skills.skillopt_webmall.leakage import _is_spec_token
    for t in ["16gb", "4k", "ddr4", "usb3", "3rd", "2x", "1920x1080", "v2", "144hz"]:
        assert _is_spec_token(t), t
    for t in ["5900x", "rtx4060", "i7", "b550"]:
        assert not _is_spec_token(t), t
