import json

import pytest

from webmall_skills.skillopt_webmall.budget import Budget, BudgetExceeded


class MockTracker:
    """Mutable tracker that yields values sequentially to simulate tracker evolution."""
    def __init__(self, values):
        self.values = list(values)
        self.idx = 0

    def __call__(self):
        if self.idx < len(self.values):
            v = self.values[self.idx]
            self.idx += 1
            return v
        # Repeat last value if we run out
        return self.values[-1]


class StatefulTracker:
    """Tracker that starts at (0, 0) then returns opt value."""
    def __init__(self, opt):
        self.opt = opt
        self.initialized = False

    def __call__(self):
        if not self.initialized:
            self.initialized = True
            return (0, 0)
        return self.opt


def make(tmp_path, opt=(0, 0), ceiling=1.0, tracker=None):
    if tracker is None:
        # Default: tracker starts at (0, 0) at init, then returns opt value
        tracker = StatefulTracker(opt)
    return Budget(tmp_path / "ledger.json", ceiling_usd=ceiling, price_input_per_m=1.0,
                  price_output_per_m=10.0, optimizer_tokens_fn=tracker)


def test_costs_and_persistence(tmp_path):
    b = make(tmp_path, opt=(100_000, 10_000))
    b.record_rollout(200_000, 5_000)            # 0.2 + 0.05 = 0.25
    s = b.spent()
    assert s["target_usd"] == pytest.approx(0.25)
    assert s["optimizer_usd"] == pytest.approx(0.2)   # 0.1 + 0.1
    assert s["total_usd"] == pytest.approx(0.45)
    assert s["rollouts"] == 1
    saved = json.loads((tmp_path / "ledger.json").read_text())
    assert saved["target_input_tokens"] == 200_000


def test_optimizer_tokens_accumulate_across_processes(tmp_path):
    # Process 1: tracker starts at (0,0), advances to (100_000, 0), saves
    # Note: save() calls _optimizer_totals twice (once for ledger, once in self.spent())
    tracker = MockTracker([(0, 0), (100_000, 0), (100_000, 0), (0, 0), (50_000, 0)])
    b1 = Budget(tmp_path / "ledger.json", ceiling_usd=1.0, price_input_per_m=1.0,
                price_output_per_m=10.0, optimizer_tokens_fn=tracker)
    b1.record_rollout(0, 0)   # init (0,0), save calls tracker twice
    # Process 2: fresh Budget loads ledger (base=100k), tracker resets and advances
    b2 = Budget(tmp_path / "ledger.json", ceiling_usd=1.0, price_input_per_m=1.0,
                price_output_per_m=10.0, optimizer_tokens_fn=tracker)
    # b2 init snapshot (0, 0), spent() calls tracker → (50_000, 0), delta=50k, total=100k+50k=150k
    assert b2.spent()["optimizer_usd"] == pytest.approx(0.15)


def test_within_process_double_counting_prevented(tmp_path):
    # Same process: Budget A saves 100k, Budget B created after, then tracker advances
    # Without fix, B would count 100k from ledger + 100k from tracker = double count
    # save() calls _optimizer_totals twice, so need values that stay at 100k then advance
    tracker = MockTracker([(0, 0), (100_000, 0), (100_000, 0), (100_000, 0), (100_000, 0), (150_000, 0)])
    b_a = Budget(tmp_path / "ledger.json", ceiling_usd=1.0, price_input_per_m=1.0,
                 price_output_per_m=10.0, optimizer_tokens_fn=tracker)
    b_a.record_rollout(0, 0)  # init (0,0), save calls tracker twice → (100_000, 0)
    # Budget B: same tracker already at 100k, snapshots init at (100_000, 0)
    b_b = Budget(tmp_path / "ledger.json", ceiling_usd=1.0, price_input_per_m=1.0,
                 price_output_per_m=10.0, optimizer_tokens_fn=tracker)
    assert b_b.spent()["optimizer_usd"] == pytest.approx(0.1)  # spent() calls tracker → (100_000, 0), delta=0
    # Tracker advances to 150k, delta now 50k, total 100k+50k=150k
    assert b_b.spent()["optimizer_usd"] == pytest.approx(0.15)  # second spent() calls tracker → (150_000, 0)


def test_optimizer_tokens_tracks_real_skillopt_tokens(tmp_path):
    from webmall_skills.skillopt_webmall.budget import optimizer_tokens
    from skillopt.model import _openai

    # Snapshot before recording anything
    before = optimizer_tokens()
    # Manually record tokens into the SkillOpt tracker (simulating real SkillOpt run)
    _openai.tracker.record("rollout", 10, 5)
    _openai.tracker.record("reflect", 3, 2)
    # Now optimizer_tokens should show the delta
    after = optimizer_tokens()
    delta_in = after[0] - before[0]
    delta_out = after[1] - before[1]
    assert delta_in == 13  # 10 + 3 from prompt_tokens
    assert delta_out == 7  # 5 + 2 from completion_tokens


def test_check_uses_observed_mean(tmp_path):
    b = make(tmp_path, ceiling=1.0)
    b.check(9)                                  # 9 x default 0.10 = 0.9 <= 1.0
    with pytest.raises(BudgetExceeded):
        b.check(11)                             # 1.1 > 1.0
    b.record_rollout(300_000, 0)                # observed 0.30 per rollout
    b.check(2)                                  # 0.3 + 0.6 = 0.9
    with pytest.raises(BudgetExceeded):
        b.check(3)                              # 0.3 + 0.9 = 1.2
