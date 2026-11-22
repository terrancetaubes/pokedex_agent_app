"""Caller authentication for /v1/chat.

Only the backend's managed identity may call the agent app. A caller must send an Entra ID access
token that:
  - is signed by the tenant (RS256, key from the tenant's JWKS),
  - has the agent's audience (AGENT_AUTH_AUDIENCE) and the tenant's v2 issuer,
  - is not expired, and
  - names an allowed caller (AGENT_ALLOWED_CALLER_APP_IDS) in the `azp` or `appid` claim.

If the auth settings are missing, every chat call is refused (503). The check fails closed.
The user's identity (`oid` from the backend header) is audit data only. It is not used here.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pokedex_agent.config import Settings

log = logging.getLogger("pokedex_agent.auth")
_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


@lru_cache(maxsize=4)
def _jwks_client(jwks_uri: str) -> jwt.PyJWKClient:
    # PyJWKClient caches the signing keys and refreshes them when needed.
    return jwt.PyJWKClient(jwks_uri)


def verify_caller_token(token: str, settings: Settings) -> dict:
    """Return the verified claims. Raise jwt.PyJWTError for a bad token, PermissionError for a wrong caller."""
    signing_key = _jwks_client(settings.jwks_uri).get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.auth_audience,
        issuer=settings.issuer,
        options={"require": ["exp", "aud", "iss"]},
    )
    caller = str(claims.get("azp") or claims.get("appid") or "")
    if caller not in settings.allowed_caller_app_ids:
        raise PermissionError("caller is not an allowed app")
    return claims


def require_caller(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    if not settings.auth_configured:
        log.error("Caller authentication is not configured. Refusing the request.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Caller authentication is not configured.",
        )
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        return verify_caller_token(credentials.credentials, settings)
    except PermissionError:
        log.warning("Rejected caller: not in the allow list.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
