from webmall_skills.skill_construction.explore_shops import evidence_name, slug_from_url, short_query


def test_slug_from_url():
    assert slug_from_url("http://localhost:8081/product/foo-bar-1/") == "foo-bar-1"
    assert slug_from_url("http://localhost:8081/cart/") is None


def test_evidence_name_is_filesystem_safe():
    assert evidence_name("shop1", "search_enter", "mouse pad") == "shop1__search_enter__mouse-pad.txt"


def test_short_query_keeps_first_two_words():
    assert short_query("Acme Ultra Widget 3000 Pro, Black") == "Acme Ultra"


def test_search_result_records_error_and_redirect():
    from webmall_skills.skill_construction.explore_shops import search_result

    obs = {"url": "http://localhost:8081/product/foo/", "last_action_error": "TimeoutError: x"}
    r = search_result(obs, 3)
    assert r["url"] == obs["url"]
    assert r["n_product_links"] == 3
    assert r["action_error"] == "TimeoutError: x"
    assert r["landed_on_product"] is True
    assert r["obs"] is obs


def test_search_result_clean_search_page():
    from webmall_skills.skill_construction.explore_shops import search_result

    r = search_result({"url": "http://localhost:8081/?s=a", "last_action_error": None}, 9)
    assert r["action_error"] == ""
    assert r["landed_on_product"] is False
