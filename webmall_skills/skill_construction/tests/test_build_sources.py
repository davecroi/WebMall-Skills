from webmall_skills.skill_construction.build_sources import (
    REDACTIONS, build_sources_md, category_descriptions, general_instruction_block,
    prompt_layout,
)
from webmall_skills.paths import REPO_ROOT
from webmall_skills.contamination import load_tasks


def test_general_block_is_shared_and_task_free():
    block = general_instruction_block()
    assert "Solution page" in block and "###" in block
    assert "<task>" not in block


def test_category_descriptions_drop_examples():
    text = category_descriptions(REPO_ROOT / "website/index.html")
    assert "Find Compatible Products" in text
    for t in load_tasks():
        assert t["task_text"] not in text


def test_category_table_has_one_row_per_category():
    text = category_descriptions(REPO_ROOT / "website/index.html")
    rows = [l for l in text.splitlines() if l.startswith("|")][2:]
    assert len(rows) == 11
    assert all(len(r.strip("|").split("|")) == 3 for r in rows)
    assert all(r.split("|")[2].strip() and r.split("|")[3].strip().isdigit() for r in rows)


def test_prompt_layout_has_no_task_or_history():
    text = prompt_layout(REPO_ROOT / "examples/task_message.txt")
    assert "# Action space" in text
    assert "Kingston" not in text
    assert "## step 0" not in text


def test_sources_md_contains_all_three_sections():
    md = build_sources_md()
    for heading in ("## 1. General task instruction",
                    "## 2. Task categories",
                    "## 3. Agent prompt layout"):
        assert heading in md


def test_redacted_phrases_are_absent():
    md = build_sources_md()
    for phrase in REDACTIONS:
        assert phrase not in md
