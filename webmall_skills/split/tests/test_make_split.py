import hashlib
import json

import pytest

from webmall_skills.paths import TASK_SETS_PATH
from webmall_skills.split.make_split import (
    SPLIT_V2_DIR, _dump_bytes, build_split, build_split_v2, load_items, write_split)


def test_counts_and_unused():
    manifest, items = build_split()
    assert {k: len(v) for k, v in items.items()} == {"train": 11, "val": 11, "test": 33}
    assert manifest["counts"] == {"train": 11, "val": 11, "test": 33, "unused": 36}
    assert len(manifest["unused"]) == 36


def test_one_one_three_per_category():
    manifest, _ = build_split()
    assert len(manifest["per_category"]) == 11
    for entry in manifest["per_category"].values():
        assert (len(entry["train"]), len(entry["val"]), len(entry["test"])) == (1, 1, 3)


def test_splits_are_disjoint_and_cover_91():
    manifest, items = build_split()
    ids = [it["id"] for split in items.values() for it in split] + manifest["unused"]
    assert len(ids) == len(set(ids)) == 91


def test_deterministic_and_seed_sensitive():
    assert build_split(seed=42) == build_split(seed=42)
    assert build_split(seed=42)[1] != build_split(seed=7)[1]


def test_manifest_records_seed_and_source_hash():
    manifest, _ = build_split()
    assert manifest["seed"] == 42
    assert manifest["source_sha256"] == hashlib.sha256(TASK_SETS_PATH.read_bytes()).hexdigest()


def test_write_split_layout_and_no_overwrite(tmp_path):
    manifest, items = build_split()
    write_split(manifest, items, tmp_path)
    assert json.loads((tmp_path / "val" / "items.json").read_text()) == items["val"]
    assert json.loads((tmp_path / "split_manifest.json").read_text())["seed"] == 42
    with pytest.raises(FileExistsError):
        write_split(manifest, items, tmp_path)
    write_split(manifest, items, tmp_path, force=True)



def test_v2_keeps_v1_and_test_unchanged():
    _, v1 = build_split()
    manifest, v2 = build_split_v2()
    assert v2["test"] == v1["test"]
    for split in ("train", "val"):
        assert {it["id"] for it in v1[split]} <= {it["id"] for it in v2[split]}
    assert manifest["counts"] == {"train": 26, "val": 21, "test": 33, "unused": 11}


def test_v2_draws_unused_in_order_and_is_disjoint():
    manifest, items = build_split_v2()
    v1 = build_split()[0]["per_category"]
    for set_id, entry in manifest["per_category"].items():
        added = entry["added"]["val"] + entry["added"]["train"]
        assert added + entry["unused"] == v1[set_id]["unused"]
    ids = [it["id"] for split in items.values() for it in split] + manifest["unused"]
    assert len(ids) == len(set(ids)) == 91
    assert build_split_v2() == (manifest, items)


def test_committed_v2_matches_builder():
    manifest, items = build_split_v2()
    assert json.loads((SPLIT_V2_DIR / "split_manifest.json").read_text()) == manifest
    for split, split_items in items.items():
        assert load_items(split) == split_items


def test_v1_rebuilt_in_memory_matches_recorded_hash():
    recorded = json.loads((SPLIT_V2_DIR / "split_manifest.json").read_text())["extends"]["manifest_sha256"]
    manifest, _ = build_split(seed=42)
    assert hashlib.sha256(_dump_bytes(manifest)).hexdigest() == recorded == (
        "339e0bea575d6e27640d5ffc94670a747a2fd334bd0f67d69d41dac11cb6e0f5")


def test_source_is_the_task_file_the_split_was_drawn_from():
    m = json.loads((SPLIT_V2_DIR / "split_manifest.json").read_text())
    assert m["source_sha256"] == hashlib.sha256(TASK_SETS_PATH.read_bytes()).hexdigest()
    assert m["counts"] == {"train": 26, "val": 21, "test": 33, "unused": 11}


def test_splits_are_disjoint():
    ids = {s: {it["id"] for it in load_items(s)} for s in ("train", "val", "test")}
    assert not (ids["train"] & ids["val"]) and not (ids["train"] & ids["test"]) and not (ids["val"] & ids["test"])
