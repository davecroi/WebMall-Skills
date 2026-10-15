from openai import OpenAI

from skillopt.model import openai_compatible_backend as backend
from webmall_skills.skillopt_webmall.openai_compat import use_max_completion_tokens


def test_renames_max_tokens_on_skillopt_clients(monkeypatch):
    sent = []
    client = OpenAI(api_key="test", base_url="http://localhost:9")
    client.chat.completions.create = lambda **kw: sent.append(kw) or "ok"
    monkeypatch.setattr(backend, "_build_client", lambda config: client)
    monkeypatch.setattr(backend, "_optimizer_client", None)
    monkeypatch.setattr(backend, "_target_client", None)

    use_max_completion_tokens()
    use_max_completion_tokens()          # idempotent: no double wrapping

    c = backend._build_client(backend.OPTIMIZER_CONFIG)
    assert c.chat.completions.create(model="gpt-6-luna", messages=[], max_tokens=7) == "ok"
    assert sent == [{"model": "gpt-6-luna", "messages": [], "max_completion_tokens": 7}]
