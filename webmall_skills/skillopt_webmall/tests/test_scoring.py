import pytest

from analyze_agentlab_results.summarize_study import calculation_results
from webmall_skills.skillopt_webmall.scoring import aggregate, read_outcome, solution_sets, task_metrics
from webmall_skills.skillopt_webmall.tests.fakes import make_step, write_fake_exp

CHECKLIST = {
    "checklist": [
        {"id": "answer1", "value": "http://s/product/a", "flag": True, "weight": 0.5},
        {"id": "answer2", "value": "http://s/product/b", "flag": False, "weight": 0.5},
        {"id": "checkpoint1", "value": "x", "flag": True, "weight": 0.1},
    ],
    "wrong_solutions": ["http://s/product/z"],
}


def test_solution_sets_counts_wrong_submissions():
    s = solution_sets(CHECKLIST, "Webmall_Find_Specific_Product_Task1")
    assert s["gold_ids"] == {"answer1", "answer2"}
    assert s["submitted"] == {"answer1", "http://s/product/z"}
    assert s["gold_urls"] == ["http://s/product/a", "http://s/product/b"]
    assert s["found_urls"] == ["http://s/product/a"]
    assert s["wrong_urls"] == ["http://s/product/z"]


def test_solution_sets_ignores_penalties_for_cart_tasks():
    s = solution_sets(CHECKLIST, "Webmall_Add_To_Cart_Task2")
    assert s["submitted"] == {"answer1"}
    assert s["wrong_urls"] == []


def test_solution_sets_without_checklist():
    s = solution_sets(None, "Webmall_Find_Specific_Product_Task1")
    assert s["gold_ids"] == set() and s["submitted"] == set()


def test_task_metrics():
    assert task_metrics({"a", "b"}, {"a", "b"}) == {"cr": 1, "precision": 1.0, "recall": 1.0, "f1": 1.0}
    m = task_metrics({"a", "b"}, {"a", "z"})
    assert m["cr"] == 0 and m["precision"] == 0.5 and m["recall"] == 0.5 and m["f1"] == 0.5
    assert task_metrics({"a"}, set()) == {"cr": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0}


def test_aggregate_matches_webmall():
    recs = [
        {"gold_ids": ["a", "b"], "submitted": ["a"]},
        {"gold_ids": ["c"], "submitted": ["c", "z"]},
    ]
    expected = calculation_results([{"a", "b"}, {"c"}], [{"a"}, {"c", "z"}])
    assert aggregate(recs) == expected


def test_read_outcome_from_fake_exp(tmp_path):
    steps = [
        make_step(0, url="http://s/", think="t0", action="fill('1', 'x')"),
        make_step(1, url="http://s/?s=x", think="t1", action="click('2')"),
        make_step(2, url="http://s/done"),
    ]
    d = write_fake_exp(tmp_path / "exp", steps, task_info=CHECKLIST,
                       summary={"n_steps": 2, "err_msg": None,
                                "stats.cum_input_tokens": 1000, "stats.cum_output_tokens": 50})
    rec = read_outcome(d, "Webmall_Find_Specific_Product_Task1")
    assert rec["cr"] == 0 and rec["recall"] == 0.5 and rec["precision"] == 0.5
    assert rec["input_tokens"] == 1000 and rec["output_tokens"] == 50
    assert rec["n_steps"] == 2 and rec["env_error"] is False
    assert rec["gold_ids"] == ["answer1", "answer2"]


def test_read_outcome_flags_env_error(tmp_path):
    d = write_fake_exp(tmp_path / "exp", [make_step(0, url="u")], task_info=None,
                       summary={"n_steps": 0, "err_msg": "NameNotFound: ..."})
    rec = read_outcome(d, "Webmall_Find_Specific_Product_Task1")
    assert rec["env_error"] is True and rec["f1"] == 0.0 and rec["cr"] == 0


def test_read_outcome_missing_summary_is_env_error(tmp_path):
    d = write_fake_exp(tmp_path / "exp", [make_step(0, url="u")], task_info=None, summary=None)
    rec = read_outcome(d, "Webmall_Find_Specific_Product_Task1")
    assert rec["env_error"] is True and rec["cr"] == 0


def test_read_outcome_reports_agentlab_cost(tmp_path):
    d = write_fake_exp(tmp_path / "exp", [make_step(0, url="u")], task_info=CHECKLIST,
                       summary={"n_steps": 0, "err_msg": None, "stats.cum_cost": 0.42})
    assert read_outcome(d, "Webmall_Find_Specific_Product_Task1")["agentlab_cost"] == 0.42
    d2 = write_fake_exp(tmp_path / "exp2", [make_step(0, url="u")], task_info=CHECKLIST,
                        summary={"n_steps": 0, "err_msg": None})
    assert read_outcome(d2, "Webmall_Find_Specific_Product_Task1")["agentlab_cost"] == 0.0


def test_read_outcome_adds_first_attempt_tokens(tmp_path):
    first = write_fake_exp(tmp_path / "first", [make_step(0, url="u")], task_info=None,
                           summary={"err_msg": "crash", "stats.cum_input_tokens": 300,
                                    "stats.cum_output_tokens": 7, "stats.cum_cost": 0.1})
    d = write_fake_exp(tmp_path / "retry", [make_step(0, url="u")], task_info=CHECKLIST,
                       summary={"n_steps": 0, "err_msg": None, "stats.cum_input_tokens": 1000,
                                "stats.cum_output_tokens": 50, "stats.cum_cost": 0.4})
    (d / "first_attempt.txt").write_text(str(first))
    rec = read_outcome(d, "Webmall_Find_Specific_Product_Task1")
    assert rec["input_tokens"] == 1300 and rec["output_tokens"] == 57
    assert rec["agentlab_cost"] == pytest.approx(0.5)
