"""Make SkillOpt's openai_compatible backend work with gpt-6-luna.

The vendored backend sends ``max_tokens``; the OpenAI API rejects it for gpt-6-luna
("Use 'max_completion_tokens' instead"). AgentLab already sends
``max_completion_tokens``. This wraps the clients SkillOpt builds so the parameter
is renamed, without editing vendored code. Call before any optimizer call.
"""
from __future__ import annotations


def _rename_max_tokens(create):
    def create_with_max_completion_tokens(**kwargs):
        if "max_tokens" in kwargs:
            kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
        return create(**kwargs)

    return create_with_max_completion_tokens


def use_max_completion_tokens() -> None:
    from skillopt.model import openai_compatible_backend as backend

    if getattr(backend._build_client, "_max_completion_tokens", False):
        return
    build = backend._build_client

    def build_client(config):
        client = build(config)
        client.chat.completions.create = _rename_max_tokens(client.chat.completions.create)
        return client

    build_client._max_completion_tokens = True
    backend._build_client = build_client
    # Drop clients built before the patch so the next call uses a wrapped one.
    backend._optimizer_client = None
    backend._target_client = None
