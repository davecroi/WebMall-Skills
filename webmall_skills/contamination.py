"""
Contamination checker for the WebMall base skill.

Builds a blocklist from the benchmark tasks (task texts, product names they
contain, expected answer URL slugs) and checks probe terms and documents
against it. See the "Design" section of webmall_skills/skill_construction/README.md.

Usage (from the repo root):
    python -m webmall_skills.contamination terms FILE
    python -m webmall_skills.contamination doc FILE [FILE...]
    python -m webmall_skills.contamination words FILE
"""

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from webmall_skills.paths import REPO_ROOT, TASK_SETS_PATH

TASK_STRINGS_PATH = REPO_ROOT / "examples/task_strings.txt"

# Words that carry no product information. Kept short on purpose: anything not
# listed here counts as task vocabulary for the strict probe-term check.
STOPWORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "by", "can", "do", "does",
    "each", "for", "from", "has", "have", "i", "if", "in", "is", "it", "its",
    "my", "of", "on", "or", "so", "that", "the", "their", "them", "these",
    "this", "to", "which", "with", "all", "find", "offer", "offers", "cheapest",
    "task", "tasks", "item", "items", "product", "products", "least", "same",
    "than", "more", "most", "one", "two", "also", "but", "not", "only", "who",
    "what", "when", "where", "will", "should", "would", "me", "we", "you",
    "your", "our", "add", "cart", "checkout", "shop", "shops", "url", "urls",
}

_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _stem(word: str) -> str:
    """Simple stemming: strip trailing 's' or 'es' to match singular/plural variants.

    Strip 'es' if word > 4 chars and ends in 'es', else strip 's' if word > 3 chars
    and ends in 's'. Then, if the result is > 3 chars and ends in 'e', strip that
    'e' too, so "microphone" and "microphones" share the stem "microphon".
    """
    if len(word) > 4 and word.endswith("es"):
        word = word[:-2]
    elif len(word) > 3 and word.endswith("s"):
        word = word[:-1]
    # normalise a trailing "e" so "microphone"/"microphones" share a stem
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]
    return word


def _strip_task_tags(text: str) -> str:
    # task texts contain a literal backslash-n, not a newline
    return re.sub(r"</?task>|\\n", " ", text).strip()


def _slug(answer: str) -> str | None:
    m = re.search(r"/product/([^/\s]+)", answer)
    return m.group(1).lower() if m else None


def load_tasks(task_sets_path: Path = TASK_SETS_PATH) -> list[dict]:
    task_sets = json.loads(Path(task_sets_path).read_text(encoding="utf-8"))
    tasks = []
    for task_set in task_sets:
        for t in task_set["tasks"]:
            correct_answer = t["correct_answer"]
            # correct_answer is already a dict (from JSON), not a string
            if isinstance(correct_answer, str):
                answers = ast.literal_eval(correct_answer).get("answers", [])
            else:
                answers = correct_answer.get("answers", [])
            tasks.append({
                "id": t["id"],
                "category": t["category"],
                "task_text": _strip_task_tags(t["task"]),
                "answer_slugs": [s for s in map(_slug, map(str, answers)) if s],
            })
    return tasks


@dataclass
class Blocklist:
    words: set[str]          # every non-stopword in any task text
    phrases: set[str]        # word 3-grams with at least two non-stopwords
    model_tokens: set[str]   # tokens mixing letters and digits, e.g. "5900x"
    slugs: set[str]          # expected answer URL slugs


def build_blocklist(task_texts: list[str], answer_slugs: list[str]) -> Blocklist:
    words, phrases, model_tokens = set(), set(), set()
    for text in task_texts:
        ws = _words(text)
        words.update(w for w in ws if w not in STOPWORDS and len(w) > 1)
        model_tokens.update(
            w for w in ws if re.search(r"[a-z]", w) and re.search(r"\d", w)
        )
        for i in range(len(ws) - 2):
            gram = ws[i:i + 3]
            if sum(w not in STOPWORDS for w in gram) >= 2:
                phrases.add(" ".join(gram))
    return Blocklist(words, phrases, model_tokens, {s.lower() for s in answer_slugs})


def _task_strings_lines(path: Path = TASK_STRINGS_PATH) -> list[str]:
    raw = [l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines()]

    def is_separator(line: str) -> bool:
        return bool(line) and set(line) <= {"-", "="}

    lines = []
    for i, line in enumerate(raw):
        if not line or is_separator(line) or re.fullmatch(r"Task \d+:", line):
            continue
        # Title and category headings are followed by a separator line; they are
        # allowed knowledge (category names), not task text.
        if i + 1 < len(raw) and is_separator(raw[i + 1]):
            continue
        lines.append(line)
    return lines


def default_blocklist() -> Blocklist:
    tasks = load_tasks()
    texts = [t["task_text"] for t in tasks] + _task_strings_lines()
    slugs = [s for t in tasks for s in t["answer_slugs"]]
    return build_blocklist(texts, slugs)


def check_term(term: str, bl: Blocklist) -> list[str]:
    """Check if term contains any blocklisted words (including singular/plural variants).

    A term word is rejected if its stem matches the stem of any blocklisted word.
    Returns the original term words that matched (not their stems).
    """
    term_words = _words(term)
    blocklist_stems = {_stem(w) for w in bl.words}
    return sorted({w for w in term_words if _stem(w) in blocklist_stems})


def check_document(text: str, bl: Blocklist) -> list[str]:
    hits = []
    lowered = text.lower()
    ws = _words(text)
    for w in sorted(set(ws) & bl.model_tokens):
        hits.append(f"model token: {w}")
    for i in range(len(ws) - 2):
        gram = " ".join(ws[i:i + 3])
        if gram in bl.phrases:
            hits.append(f"phrase: {gram}")
    for slug in sorted(bl.slugs):
        if slug in lowered:
            hits.append(f"answer slug: {slug}")
    return sorted(set(hits))


def word_overlap(text: str, bl: Blocklist) -> list[str]:
    """Report mode (manual sign-off, never affects exit status): every distinct
    word of the document whose stem matches a blocklisted word's stem."""
    stems = {_stem(w) for w in bl.words}
    return sorted({w for w in _words(text) if _stem(w) in stems})


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"terms", "doc", "words"}:
        print("usage: python -m webmall_skills.contamination terms FILE | doc FILE [FILE...] | words FILE")
        return 2
    bl = default_blocklist()
    failed = False
    if argv[0] == "terms":
        for term in Path(argv[1]).read_text(encoding="utf-8").splitlines():
            term = term.split("#", 1)[0].strip()
            if not term:
                continue
            overlap = check_term(term, bl)
            print(f"{'REJECT' if overlap else 'ok    '} {term}" + (f"  {overlap}" if overlap else ""))
            failed |= bool(overlap)
    elif argv[0] == "words":
        words = word_overlap(Path(argv[1]).read_text(encoding="utf-8"), bl)
        print(f"{argv[1]}: {len(words)} word(s) overlapping the blocklist (manual sign-off)")
        for w in words:
            print(f"  {w}")
        return 0
    else:
        for path in argv[1:]:
            hits = check_document(Path(path).read_text(encoding="utf-8"), bl)
            print(f"{path}: {len(hits)} hit(s)")
            for h in hits:
                print(f"  {h}")
            failed |= bool(hits)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
