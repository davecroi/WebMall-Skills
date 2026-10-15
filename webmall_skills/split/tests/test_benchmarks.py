import json

from webmall_skills.split.benchmarks import SPLIT_BENCHMARKS, split_task_names
from webmall_skills.split.make_split import SPLIT_V2_DIR


def _ids(split_dir, split):
    return [it["id"] for it in json.loads((split_dir / split / "items.json").read_text())]


def test_test_benchmark_is_exactly_the_test_split():
    names = split_task_names("test")
    assert names == [f"webmall.{i}" for i in _ids(SPLIT_V2_DIR, "test")]
    assert len(names) == len(set(names)) == 33


def test_test_benchmark_has_no_train_or_val_tasks():
    test = set(split_task_names("test"))
    assert not test & set(split_task_names("train"))
    assert not test & set(split_task_names("val"))


def test_test_benchmark_builds_registered_tasks():
    bench = SPLIT_BENCHMARKS["webmall_skills_test"]()
    assert bench.name == "webmall_skills_test"
    assert [e.task_name for e in bench.env_args_list] == split_task_names("test")
    assert all(e.max_steps == 50 for e in bench.env_args_list)
    assert set(split_task_names("test")) <= set(bench.task_metadata["task_name"])


def test_register_adds_split_benchmarks():
    from webmall_overrides.configs import WEBMALL_BENCHMARKS
    from webmall_skills.split.benchmarks import register
    register()
    assert {"webmall_skills_train", "webmall_skills_val", "webmall_skills_test"} <= set(WEBMALL_BENCHMARKS)
