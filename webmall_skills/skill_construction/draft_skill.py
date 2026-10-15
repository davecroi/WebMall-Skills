"""One API call to gpt-6.1-sol that drafts the base skill.

Usage (from the repo root): python -m webmall_skills.skill_construction.draft_skill
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from webmall_skills.paths import REPO_ROOT, SKILLS_DIR

CONSTRUCTION_DIR = SKILLS_DIR / "base/construction"
MODEL = "gpt-6.1-sol"
REASONING_EFFORT = "high"  # temperature is fixed at 1 by the model and not sent


def build_request(prompt: str, sources: str, findings: str) -> dict:
    content = (
        f"{prompt.strip()}\n\n"
        f"===== SOURCES =====\n{sources.strip()}\n\n"
        f"===== FINDINGS =====\n{findings.strip()}\n"
    )
    return {
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "max_completion_tokens": 32_000,
        "messages": [{"role": "user", "content": content}],
    }


def run() -> Path:
    load_dotenv(REPO_ROOT / ".env")
    read = lambda name: (CONSTRUCTION_DIR / name).read_text(encoding="utf-8")
    request = build_request(read("draft_prompt.md"), read("sources.md"), read("findings.md"))
    (CONSTRUCTION_DIR / "draft_request.json").write_text(
        json.dumps(request, indent=2),
        encoding="utf-8",
    )
    response = OpenAI().chat.completions.create(**request)
    (CONSTRUCTION_DIR / "draft_response.json").write_text(
        response.model_dump_json(indent=2), encoding="utf-8"
    )
    draft = CONSTRUCTION_DIR / "draft_SKILL.md"
    draft.write_text(response.choices[0].message.content, encoding="utf-8")
    return draft


if __name__ == "__main__":
    print(f"wrote {run()}")
