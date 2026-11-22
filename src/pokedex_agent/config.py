"""Settings loaded from environment variables. Holds no secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    key_vault_url: str | None
    max_tool_calls_per_request: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        max_calls = int(os.environ.get("POKEDEX_MAX_TOOL_CALLS", "5"))
        if max_calls < 1 or max_calls > 20:
            raise ValueError("POKEDEX_MAX_TOOL_CALLS must be between 1 and 20")
        return cls(
            key_vault_url=os.environ.get("KEY_VAULT_URL") or None,
            max_tool_calls_per_request=max_calls,
            log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        )
