from webmall_skills.contamination import (
    _stem, build_blocklist, check_document, check_term, default_blocklist,
    load_tasks, word_overlap,
)

TASKS = [
    "Find all offers for the Zorblax 9000X Turbo.",
    "Find the cheapest offer for a Quibble QB-12 phone case.",
]
SLUGS = ["zorblax-9000x-turbo-3-7-ghz"]


def bl():
    return build_blocklist(TASKS, SLUGS)


def test_term_sharing_task_word_is_rejected():
    assert check_term("turbo fan", bl()) == ["turbo"]


def test_term_with_only_stopwords_or_generic_words_passes():
    assert check_term("the offers", bl()) == []
    assert check_term("webcam", bl()) == []


def test_document_hits_model_token_phrase_and_slug():
    text = "Look for the 9000x. Quibble QB-12 phone case. /product/zorblax-9000x-turbo-3-7-ghz"
    hits = check_document(text, bl())
    assert any("9000x" in h for h in hits)
    assert any("quibble qb 12" in h for h in hits)
    assert any("zorblax-9000x-turbo-3-7-ghz" in h for h in hits)


def test_clean_document_has_no_hits():
    assert check_document("Search each shop with short keywords.", bl()) == []


def test_real_task_file_loads_91_tasks_with_answers():
    tasks = load_tasks()
    assert len(tasks) == 91
    assert all(t["task_text"] for t in tasks)
    assert sum(len(t["answer_slugs"]) for t in tasks) > 50


def test_default_blocklist_rejects_a_real_task_product():
    assert check_term("ryzen", default_blocklist()) == ["ryzen"]


def test_task_strings_lines_skip_headings(tmp_path):
    from webmall_skills.contamination import _task_strings_lines
    f = tmp_path / "task_strings.txt"
    f.write_text(
        "SOME TITLE\n=====\n\nCategory Heading\n-----\n\nTask 1:\n\nFind the thing.\n",
        encoding="utf-8",
    )
    assert _task_strings_lines(f) == ["Find the thing."]


def test_term_rejects_singular_when_task_has_plural():
    """Singular form of term word should be rejected if task has the plural."""
    # Task text contains "tablets" (plural)
    blocklist = build_blocklist(["Find all offers for Widgets and tablets."], [])
    # Term contains "tablet" (singular) - should be rejected
    assert check_term("tablet stand", blocklist) == ["tablet"]


def test_term_rejects_plural_when_task_has_singular():
    """Plural form of term word should be rejected if task has the singular."""
    # Task text contains "widget" (singular)
    blocklist = build_blocklist(["Find the widget for sale."], [])
    # Term contains "widgets" (plural) - should be rejected
    assert check_term("widgets organizer", blocklist) == ["widgets"]


def test_stem_shares_stem_for_e_ending_plurals():
    assert _stem("microphone") == _stem("microphones")
    assert _stem("price") == _stem("prices")


def test_word_overlap_lists_single_word_matches_but_doc_mode_stays_silent():
    b = bl()
    text = "Prefer a turbo option. Zorblaxes are listed. Search each shop."
    assert word_overlap(text, b) == ["turbo", "zorblaxes"] or word_overlap(text, b) == ["turbo"]
    assert "turbo" in word_overlap(text, b)
    assert check_document("Prefer a turbo option.", b) == []
    assert word_overlap("Search each shop with short keywords.", b) == []
