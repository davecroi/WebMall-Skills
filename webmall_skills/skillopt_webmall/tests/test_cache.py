from webmall_skills.skillopt_webmall.cache import RolloutCache


def test_roundtrip_and_misses(tmp_path):
    c = RolloutCache(tmp_path)
    assert c.get("skill A", "T1", 0) is None
    c.put("skill A", "T1", 0, {"f1": 0.5})
    assert c.get("skill A", "T1", 0) == {"f1": 0.5}
    assert c.get("skill A", "T1", 1) is None          # other repeat
    assert c.get("skill A", "T2", 0) is None          # other task
    assert c.get("skill A.", "T1", 0) is None         # one-character change
    assert RolloutCache(tmp_path).get("skill A", "T1", 0) == {"f1": 0.5}  # persisted


def test_noskill_key(tmp_path):
    c = RolloutCache(tmp_path)
    c.put(None, "T1", 0, {"f1": 0.1})
    assert RolloutCache.skill_key(None) == "noskill"
    assert c.get(None, "T1", 0) == {"f1": 0.1}
    assert c.get("", "T1", 0) == {"f1": 0.1}


def test_put_is_atomic_and_leaves_no_tmp(tmp_path):
    c = RolloutCache(tmp_path)
    c.put("skill A", "T1", 0, {"f1": 0.5})
    c.put("skill A", "T1", 0, {"f1": 0.7})
    assert c.get("skill A", "T1", 0) == {"f1": 0.7}
    assert [p for p in tmp_path.rglob("*") if p.is_file() and p.suffix != ".json"] == []
