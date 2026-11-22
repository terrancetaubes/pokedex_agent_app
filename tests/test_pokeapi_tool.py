import pytest

from pokedex_agent.tools import pokeapi_tool
from pokedex_agent.tools.pokeapi import PokemonNotFoundError


@pytest.mark.parametrize("bad_id", [0, -1, "25", 2.5, True, None])
def test_run_tool_rejects_invalid_ids_without_calling_api(monkeypatch, bad_id):
    def fail(_):
        raise AssertionError("API must not be called for an invalid ID")

    monkeypatch.setattr(pokeapi_tool, "get_pokeapi_data", fail)
    result = pokeapi_tool.run_tool(bad_id)
    assert result["ok"] is False
    assert "error" in result


def test_run_tool_success(monkeypatch):
    monkeypatch.setattr(pokeapi_tool, "get_pokeapi_data", lambda i: {"id": i, "is_baby": False})
    assert pokeapi_tool.run_tool(25) == {"ok": True, "data": {"id": 25, "is_baby": False}}


def test_run_tool_unknown_species(monkeypatch):
    def not_found(_):
        raise PokemonNotFoundError("PokeAPI has no species record for ID 99999.")

    monkeypatch.setattr(pokeapi_tool, "get_pokeapi_data", not_found)
    result = pokeapi_tool.run_tool(99999)
    assert result == {"ok": False, "error": "PokeAPI has no species record for ID 99999."}


def test_run_tool_outage_returns_safe_message(monkeypatch):
    import requests

    def down(_):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(pokeapi_tool, "get_pokeapi_data", down)
    result = pokeapi_tool.run_tool(25)
    assert result["ok"] is False
    assert "boom" not in result["error"]


def test_tool_spec_matches_function_name():
    assert pokeapi_tool.TOOL_SPEC["name"] == pokeapi_tool.TOOL_NAME
    assert pokeapi_tool.TOOL_SPEC["parameters"]["required"] == ["pokeapi_id"]
