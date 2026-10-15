"""Synthetic AgentLab experiment folders for tests (no browser needed)."""
import gzip
import json
import pickle
from pathlib import Path
from types import SimpleNamespace


def make_step(i, url="", think="", memory="", action=None, error="", axtree="",
              task_info=None):
    content = f"<think>\n{think}\n</think>\n\n<memory>\n{memory}\n</memory>\n\n<action>\n{action}\n</action>"
    agent_info = (
        SimpleNamespace(think=think, chat_messages=[{"role": "assistant", "content": content}])
        if action else {}
    )
    return SimpleNamespace(
        step=i, action=action, agent_info=agent_info, task_info=task_info,
        obs={"url": url, "axtree_txt": axtree, "last_action_error": error},
    )


def write_fake_exp(directory, steps, task_info=None, summary=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(steps):
        if i == len(steps) - 1:
            s.task_info = task_info
        with gzip.open(directory / f"step_{i}.pkl.gz", "wb") as f:
            pickle.dump(s, f)
    if summary is not None:
        (directory / "summary_info.json").write_text(json.dumps(summary))
    return directory
