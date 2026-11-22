import pytest

from pokedex_agent.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("POKEDEX_MAX_TOOL_CALLS", raising=False)
    settings = Settings.from_env()
    assert settings.max_tool_calls_per_request == 5


def test_tool_call_limit_is_enforced(monkeypatch):
    monkeypatch.setenv("POKEDEX_MAX_TOOL_CALLS", "0")
    with pytest.raises(ValueError):
        Settings.from_env()
