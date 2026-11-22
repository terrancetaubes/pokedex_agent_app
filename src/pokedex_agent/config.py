"""Settings loaded from environment variables. Holds no secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    key_vault_url: str | None
    max_tool_calls_per_request: int
    log_level: str
    # Caller authentication for /v1/chat. All three must be set, or every chat call is refused.
    tenant_id: str | None
    auth_audience: str | None  # for example api://pokedex-agent
    allowed_caller_app_ids: tuple[str, ...]  # client IDs of the managed identities allowed to call

    @property
    def auth_configured(self) -> bool:
        return bool(self.tenant_id and self.auth_audience and self.allowed_caller_app_ids)

    @property
    def issuer(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def jwks_uri(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"

    @classmethod
    def from_env(cls) -> Settings:
        max_calls = int(os.environ.get("POKEDEX_MAX_TOOL_CALLS", "5"))
        if max_calls < 1 or max_calls > 20:
            raise ValueError("POKEDEX_MAX_TOOL_CALLS must be between 1 and 20")
        callers = tuple(
            c.strip()
            for c in os.environ.get("AGENT_ALLOWED_CALLER_APP_IDS", "").split(",")
            if c.strip()
        )
        return cls(
            key_vault_url=os.environ.get("KEY_VAULT_URL") or None,
            max_tool_calls_per_request=max_calls,
            log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            tenant_id=os.environ.get("AZURE_TENANT_ID") or None,
            auth_audience=os.environ.get("AGENT_AUTH_AUDIENCE") or None,
            allowed_caller_app_ids=callers,
        )
