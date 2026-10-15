import json

import pytest

from webmall_skills.skillopt_webmall import runner


@pytest.fixture(autouse=True)
def fake_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_make_exp_args_matches_benchmark_settings():
    agent = runner.build_agent("Skill text", "so1")
    exps = runner.make_exp_args(["Webmall_Checkout_Task1", "Webmall_Find_Cheapest_Offer_Task2"], agent)
    assert [e.env_args.task_name for e in exps] == [
        "webmall.Webmall_Checkout_Task1", "webmall.Webmall_Find_Cheapest_Offer_Task2"]
    assert all(e.env_args.max_steps == runner.MAX_STEPS == 50 for e in exps)
    assert all(e.env_args.headless for e in exps)
    assert exps[0].agent_args.skill_text == "Skill text"


def test_build_agent_without_skill_does_not_mutate_shared_agent():
    from webmall_skills.skillopt_webmall.agent_config import AGENT_GPT6_LUNA_AX_M
    a = runner.build_agent(None, "noskill")
    assert a is not AGENT_GPT6_LUNA_AX_M
    assert not hasattr(a, "skill_text") or a.skill_text is None


def test_build_agent_with_skill_does_not_share_flags():
    from webmall_skills.skillopt_webmall.agent_config import AGENT_GPT6_LUNA_AX_M
    a = runner.build_agent("Skill text", "so1")
    assert a.flags is not AGENT_GPT6_LUNA_AX_M.flags


def test_run_tasks_rejects_duplicate_ids(tmp_path, monkeypatch):
    def boom(**kw):
        raise AssertionError("run_experiments must not be called")
    monkeypatch.setattr(runner, "run_experiments", boom)
    with pytest.raises(ValueError, match="duplicate task ids"):
        runner.run_tasks(["Webmall_Checkout_Task1", "Webmall_Checkout_Task1"], "s", "so1", tmp_path)


def test_has_env_error(tmp_path):
    ok = tmp_path / "ok"; ok.mkdir()
    (ok / "summary_info.json").write_text(json.dumps({"err_msg": None}))
    bad = tmp_path / "bad"; bad.mkdir()
    (bad / "summary_info.json").write_text(json.dumps({"err_msg": "boom"}))
    missing = tmp_path / "missing"; missing.mkdir()
    assert runner.has_env_error(ok) is False
    assert runner.has_env_error(bad) is True
    assert runner.has_env_error(missing) is True


def test_run_tasks_relaunches_env_errors_once(tmp_path, monkeypatch):
    calls = []

    def fake_run(n_jobs, exp_args_list, study_dir, parallel_backend):
        calls.append([e.env_args.task_name for e in exp_args_list])
        for e in exp_args_list:
            e.exp_dir = tmp_path / f"{len(calls)}_{e.env_args.task_name}"
            e.exp_dir.mkdir()
            failed_first_time = len(calls) == 1 and e.env_args.task_name.endswith("Task2")
            (e.exp_dir / "summary_info.json").write_text(
                json.dumps({"err_msg": "crash" if failed_first_time else None}))

    monkeypatch.setattr(runner, "run_experiments", fake_run)
    dirs = runner.run_tasks(["Webmall_Checkout_Task1", "Webmall_Checkout_Task2"],
                            "skill", "so1", tmp_path / "study")
    assert calls == [["webmall.Webmall_Checkout_Task1", "webmall.Webmall_Checkout_Task2"],
                     ["webmall.Webmall_Checkout_Task2"]]
    assert dirs["Webmall_Checkout_Task2"].name.startswith("2_")
    assert runner.has_env_error(dirs["Webmall_Checkout_Task2"]) is False


def test_relaunched_dir_records_first_attempt(tmp_path, monkeypatch):
    n = []

    def fake_run(n_jobs, exp_args_list, study_dir, parallel_backend):
        n.append(1)
        for e in exp_args_list:
            e.exp_dir = tmp_path / f"{len(n)}_{e.env_args.task_name}"
            e.exp_dir.mkdir()
            (e.exp_dir / "summary_info.json").write_text(
                json.dumps({"err_msg": "crash" if len(n) == 1 else None}))

    monkeypatch.setattr(runner, "run_experiments", fake_run)
    dirs = runner.run_tasks(["Webmall_Checkout_Task1", "Webmall_Checkout_Task2"],
                            "skill", "so1", tmp_path / "study")
    for d in dirs.values():
        assert d.name.startswith("2_")
    assert (dirs["Webmall_Checkout_Task1"] / "first_attempt.txt").read_text() == str(
        tmp_path / "1_webmall.Webmall_Checkout_Task1")
