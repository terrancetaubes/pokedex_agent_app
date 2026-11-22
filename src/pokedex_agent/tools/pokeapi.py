from __future__ import annotations

from typing import Any

import requests

pokeapi_graphql_url = "https://graphql.pokeapi.co/v1beta2"

query_template = """
query GetPokemonTraitsById($id: Int!) {
  pokemonspecies(where: { id: { _eq: $id } }) {
    id
    is_baby
    is_legendary
    is_mythical
    has_gender_differences
    pokemoncolor {
      name
    }
    pokemonshape {
      name
    }
    pokemonhabitat {
      name
    }
  }
}
"""


class PokemonNotFoundError(Exception):
    """Raised when the requested Pokemon species ID does not exist."""


# =============================================================================
# PRIMARY FUNCTION: Query PokeAPI GraphQL and return one species record.
# =============================================================================
def get_pokeapi_data(pokemon_id: int) -> dict[str, Any]:
    """Return species traits for the supplied PokeAPI species ID."""
    payload = {"query": query_template, "variables": {"id": pokemon_id}}
    response = requests.post(pokeapi_graphql_url, json=payload, timeout=30)
    response.raise_for_status()

    response_data = response.json()
    if response_data.get("errors"):
        raise RuntimeError(
            f"PokeAPI GraphQL returned errors: {response_data['errors']}"
        )

    species_records = (
        response_data.get("data", {}).get("pokemonspecies") or []
    )
    if not species_records:
        raise PokemonNotFoundError(
            f"PokeAPI has no species record for ID {pokemon_id}."
        )

    return species_records[0]
