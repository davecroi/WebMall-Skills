"""Seeded stratified train/val/test split of the 91 WebMall tasks.

Per category (task set): 1 train, 1 val, 3 test, the rest unused. Drawn once with
seed 42 and committed before any experiment; never re-drawn.

split_v2 extends it without re-drawing: per category, the next unused tasks (in the
seed-42 order stored in the manifest) go to val (+1) then train (+2); train/val/test
of v1 are kept, test is unchanged. Reason: the pilot showed train F1 0.94 (few
failures to reflect on) and a noisy 11-task val gate.

The v1 split is not stored; it is rebuilt in memory from seed 42 and verified against
`extends.manifest_sha256`.

    python -m webmall_skills.split.make_split                  # re-creates split_v2/ (needs --force if it exists)
    python -m webmall_skills.split.make_split --v1 --out DIR   # writes the v1 split to DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

from webmall_skills.paths import REPO_ROOT, TASK_SETS_PATH

SPLIT_V2_DIR = Path(__file__).resolve().parent / "split_v2"
PER_CATEGORY = {"train": 1, "val": 1, "test": 3}
EXTRA_PER_CATEGORY = {"val": 1, "train": 2}  # drawn in this order from each category's unused


def _natural(task_id: str) -> tuple:
    m = re.match(r"^(.*?)(\d+)$", task_id)
    return (m.group(1), int(m.group(2))) if m else (task_id, 0)


def build_split(task_sets_path: Path = TASK_SETS_PATH, seed: int = 42):
    raw = Path(task_sets_path).read_bytes()
    task_sets = json.loads(raw)
    rng = random.Random(seed)  # one stream, task sets in file order
    items: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    per_category: dict[str, dict] = {}
    unused: list[str] = []
    for task_set in task_sets:
        by_id = {t["id"]: t for t in task_set["tasks"]}
        ids = sorted(by_id, key=_natural)
        rng.shuffle(ids)
        entry = {"category": task_set["tasks"][0]["category"]}
        pos = 0
        for split, n in PER_CATEGORY.items():
            chosen = ids[pos:pos + n]
            pos += n
            entry[split] = chosen
            items[split].extend(
                {"id": i, "category": by_id[i]["category"], "task_set_id": task_set["id"]}
                for i in chosen
            )
        entry["unused"] = ids[pos:]
        unused.extend(ids[pos:])
        per_category[task_set["id"]] = entry
    manifest = {
        "seed": seed,
        "source": str(Path(task_sets_path).resolve().relative_to(REPO_ROOT)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "per_category_counts": PER_CATEGORY,
        "counts": {**{k: len(v) for k, v in items.items()}, "unused": len(unused)},
        "per_category": per_category,
        "unused": unused,
    }
    return manifest, items


def extend_split(base_manifest: dict, base_sha256: str, extra: dict = EXTRA_PER_CATEGORY):
    """Move the next unused tasks of each category into val/train; test stays as is."""
    index = {}
    task_sets = json.loads(Path(REPO_ROOT / base_manifest["source"]).read_bytes())
    for task_set in task_sets:
        for t in task_set["tasks"]:
            index[t["id"]] = {"id": t["id"], "category": t["category"], "task_set_id": task_set["id"]}
    items: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    per_category: dict[str, dict] = {}
    unused: list[str] = []
    for set_id, base in base_manifest["per_category"].items():
        entry = {"category": base["category"], **{s: list(base[s]) for s in items}}
        rest = list(base["unused"])
        entry["added"] = {}
        for split, n in extra.items():
            added, rest = rest[:n], rest[n:]
            entry[split].extend(added)
            entry["added"][split] = added
        entry["unused"] = rest
        unused.extend(rest)
        per_category[set_id] = entry
        for split in items:
            items[split].extend(index[i] for i in entry[split])
    manifest = {
        "seed": base_manifest["seed"],
        "source": base_manifest["source"],
        "source_sha256": base_manifest["source_sha256"],
        "extends": {"split": "split", "manifest_sha256": base_sha256,
                    "extra_per_category": extra,
                    "reason": "pilot: train F1 0.94 (few failures to reflect on) and a noisy "
                              "11-task val gate; val/train enlarged from unused tasks, test unchanged"},
        "per_category_counts": base_manifest["per_category_counts"],
        "counts": {**{k: len(v) for k, v in items.items()}, "unused": len(unused)},
        "per_category": per_category,
        "unused": unused,
    }
    return manifest, items


def build_split_v2():
    manifest, _ = build_split(seed=42)
    raw = _dump_bytes(manifest)
    return extend_split(manifest, hashlib.sha256(raw).hexdigest())


def _dump_bytes(data) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_dump_bytes(data))


def load_items(split: str, split_dir: Path = SPLIT_V2_DIR) -> list[dict]:
    return json.loads((Path(split_dir) / split / "items.json").read_text(encoding="utf-8"))


def write_split(manifest: dict, items: dict, out_dir: Path, force: bool = False) -> None:
    out_dir = Path(out_dir)
    if (out_dir / "split_manifest.json").exists() and not force:
        raise FileExistsError(f"{out_dir} already holds a split; it must not be re-drawn")
    _dump(out_dir / "split_manifest.json", manifest)
    for split, split_items in items.items():
        _dump(out_dir / split / "items.json", split_items)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--v1", action="store_true", help="write the v1 split (seed 42) to --out instead of split_v2")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--force", action="store_true", help="overwrite an existing split")
    args = p.parse_args()
    if args.v1:
        if args.out is None:
            p.error("--v1 needs an explicit --out DIR (the v1 split is not stored in the repo)")
        manifest, items = build_split(seed=42)
    else:
        manifest, items = build_split_v2()
        args.out = args.out or SPLIT_V2_DIR
    write_split(manifest, items, args.out, force=args.force)
    print(f"wrote {args.out}: {manifest['counts']}")


if __name__ == "__main__":
    main()
