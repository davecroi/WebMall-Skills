"""One OpenRouter call to deepseek/deepseek-v4.1-flash that drafts the base skill.

Usage (from the repo root): python -m webmall_skills.skill_construction.draft_skill
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from webmall_skills.paths import REPO_ROOT, SKILLS_DIR

CONSTRUCTION_DIR = SKILLS_DIR / "base/construction"
MODEL = "deepseek/deepseek-v4.1-flash"
REASONING_EFFORT = "high"  # temperature not sent: provider default
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


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
        "extra_body": {"provider": {"sort": "price"}},
    }


def run() -> Path:
    load_dotenv(REPO_ROOT / ".env")
    read = lambda name: (CONSTRUCTION_DIR / name).read_text(encoding="utf-8")
    request = build_request(read("draft_prompt.md"), read("sources.md"), read("findings.md"))
    (CONSTRUCTION_DIR / "draft_request.json").write_text(
        json.dumps(request, indent=2),
        encoding="utf-8",
    )
    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=OPENROUTER_BASE_URL)
    response = client.chat.completions.create(**request)
    (CONSTRUCTION_DIR / "draft_response.json").write_text(
        response.model_dump_json(indent=2), encoding="utf-8"
    )
    draft = CONSTRUCTION_DIR / "draft_SKILL.md"
    draft.write_text(response.choices[0].message.content, encoding="utf-8")
    return draft


if __name__ == "__main__":
    print(f"wrote {run()}")
