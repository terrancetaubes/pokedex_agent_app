"""Agent tool: PokeAPI species traits.

Runs in-process. The agent calls run_tool() with the arguments described by
TOOL_SPEC. The function never raises for expected failures. It returns a dict
the agent can read:
  {"ok": True,  "data": {...}}      on success
  {"ok": False, "error": "..."}     on a bad ID, an unknown species, or an outage
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from pokedex_agent.tools.pokeapi import PokemonNotFoundError, get_pokeapi_data

log = logging.getLogger(__name__)

TOOL_NAME = "get_pokemon_species_traits"

TOOL_SPEC: dict[str, Any] = {
    "name": TOOL_NAME,
    "description": (
        "Return species traits for one Pokemon from PokeAPI: baby, legendary, "
        "and mythical status, gender differences, color, shape, and habitat. "
        "Use the PokeAPI species ID, which is not always the Pokedex number."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "pokeapi_id": {
                "type": "integer",
                "minimum": 1,
                "description": "Positive PokeAPI species ID.",
            }
        },
        "required": ["pokeapi_id"],
        "additionalProperties": False,
    },
}


def _validate_id(pokeapi_id: Any) -> int:
    # bool is a subclass of int in Python. Reject it explicitly.
    if isinstance(pokeapi_id, bool) or not isinstance(pokeapi_id, int):
        raise TypeError("pokeapi_id must be an integer.")
    if pokeapi_id < 1:
        raise ValueError("pokeapi_id must be a positive integer.")
    return pokeapi_id


def run_tool(pokeapi_id: Any) -> dict[str, Any]:
    """Look up species traits. Return a result dict. See module docstring."""
    try:
        valid_id = _validate_id(pokeapi_id)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}

    try:
        return {"ok": True, "data": get_pokeapi_data(valid_id)}
    except PokemonNotFoundError as exc:
        return {"ok": False, "error": str(exc)}
    except (requests.RequestException, RuntimeError):
        log.exception("PokeAPI lookup failed for id=%s", valid_id)
        return {"ok": False, "error": "PokeAPI is unavailable. Try again later."}
