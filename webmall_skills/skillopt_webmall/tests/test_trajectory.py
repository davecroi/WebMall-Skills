from skillopt.gradient.reflect import fmt_trajectory

from webmall_skills.skillopt_webmall.tests.fakes import make_step, write_fake_exp
from webmall_skills.skillopt_webmall.trajectory import StepView, build_conversation, load_steps, tree_steps
from webmall_skills.skillopt_webmall import trajectory


def sv(i, url, action="click('1')", error="", axtree="TREE"):
    return StepView(step=i, url=url, think=f"t{i}", memory="", action=action, error=error, axtree=axtree)


def test_load_steps_reads_think_memory_and_next_error(tmp_path):
    steps = [
        make_step(0, url="http://a", think="search", memory="note", action="fill('3','x')", axtree="T0"),
        make_step(1, url="http://a?s=x", think="open", action="click('9')", error="", axtree="T1"),
        make_step(2, url="http://a?s=x", error="TimeoutError"),
    ]
    views = load_steps(write_fake_exp(tmp_path / "e", steps))
    assert [v.action for v in views] == ["fill('3','x')", "click('9')", None]
    assert views[0].memory == "note" and views[0].think == "search"
    assert views[1].error == "TimeoutError"   # error of action at step 1 is in obs of step 2
    assert views[0].error == ""


def test_tree_steps_navigation_errors_and_last_two():
    steps = [
        sv(0, "u0"), sv(1, "u0"), sv(2, "u1"), sv(3, "u1", error="boom"),
        sv(4, "u1"), sv(5, "u1"), sv(6, "u1"), sv(7, "u1", action=None),
    ]
    # 2: url changed; 3: error; 5, 6: last two acting steps; 0 and 1, 4 excluded
    assert tree_steps(steps) == {2, 3, 5, 6}


def test_build_conversation_caps_trees_and_ends_with_evaluation():
    long_tree = "x" * (trajectory.AXTREE_CHAR_CAP + 500)
    steps = [sv(0, "u0", axtree=long_tree), sv(1, "u1", axtree=long_tree), sv(2, "u1", action=None)]
    outcome = {"cr": 0, "precision": 1.0, "recall": 0.5, "f1": 0.667,
               "gold_urls": ["g1", "g2"], "found_urls": ["g1"], "wrong_urls": []}
    conv = build_conversation(steps, "Find all offers for X.", outcome)
    assert conv[0] == {"role": "user", "content": "Task: Find all offers for X."}
    trees = [c for c in conv if c.get("role") == "observation"]
    assert len(trees) == 2
    assert all(len(c["content"]) < trajectory.AXTREE_CHAR_CAP + 300 for c in trees)
    acts = [c for c in conv if "action" in c]
    assert [c["action"] for c in acts] == ["click('1')", "click('1')"]
    last = conv[-1]
    assert last["role"] == "system"
    assert "g2" in last["content"] and "F1=0.67" in last["content"]
    text = fmt_trajectory(conv)          # SkillOpt can render it
    assert "[verification]" in text and "[step 0 action]" in text


def test_tree_budget_prioritises_errors_last_steps_and_search_pages(monkeypatch):
    """Test exact budget-driven selection: tiers, stop-at-first-misfit, chronological tier-4, empty skip.

    Hand-computed scenario: TREE_CHAR_BUDGET=30000, AXTREE_CHAR_CAP=8000.
    Tier1 {6}→22k rem; Tier2 {7,8}→18k rem; Tier3 {1}→10k rem;
    Tier4 chron: 2 fits(rem 2k)→skip 3(empty)→skip 4(3k>2k)→5 fits(rem 500k).
    Expected: {1,2,5,6,7,8}. Excluded: 0(no nav), 3(empty), 4(misfit), 9(no action).
    """
    monkeypatch.setattr(trajectory, "TREE_CHAR_BUDGET", 30_000)

    steps = [
        StepView(step=0, url="http://s1/", think="t0", memory="", action="click('1')", error="", axtree="x"*8000),
        StepView(step=1, url="http://s1/?s=a", think="t1", memory="", action="click('1')", error="", axtree="x"*8000),
        StepView(step=2, url="http://s1/p/x", think="t2", memory="", action="click('1')", error="", axtree="x"*8000),
        StepView(step=3, url="http://s1/p/y", think="t3", memory="", action="click('1')", error="", axtree=""),
        StepView(step=4, url="http://s1/p/z", think="t4", memory="", action="click('1')", error="", axtree="x"*3000),
        StepView(step=5, url="http://s1/p/w", think="t5", memory="", action="click('1')", error="", axtree="x"*1500),
        StepView(step=6, url="http://s1/p/w", think="t6", memory="", action="click('1')", error="boom", axtree="x"*8000),
        StepView(step=7, url="http://s1/p/w", think="t7", memory="", action="click('1')", error="", axtree="x"*2000),
        StepView(step=8, url="http://s1/p/w", think="t8", memory="", action="click('1')", error="", axtree="x"*2000),
        StepView(step=9, url="http://s1/p/w", think="t9", memory="", action=None, error="", axtree=""),
    ]

    assert tree_steps(steps) == {1, 2, 5, 6, 7, 8}
    # Excluded: 0 (no URL change from prev), 3 (empty axtree), 4 (doesn't fit, stops at first misfit), 9 (no action)
