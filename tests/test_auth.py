"""Caller-auth tests. They sign tokens with a test RSA key, so no Entra ID call is made."""

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from pokedex_agent import auth
from pokedex_agent.api import app
from pokedex_agent.auth import get_settings
from pokedex_agent.config import Settings

TENANT = "00000000-0000-0000-0000-000000000000"
AUDIENCE = "api://pokedex-agent"
ALLOWED_CALLER = "11111111-1111-1111-1111-111111111111"
ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"


def _key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


SIGNING_KEY = _key()
OTHER_KEY = _key()


class _FakeSigningKey:
    def __init__(self, key):
        self.key = key


class _FakeJwks:
    def get_signing_key_from_jwt(self, token):
        return _FakeSigningKey(SIGNING_KEY.public_key())


@pytest.fixture(autouse=True)
def _fake_jwks(monkeypatch):
    monkeypatch.setattr(auth, "_jwks_client", lambda uri: _FakeJwks())


@pytest.fixture
def settings():
    return Settings(
        key_vault_url=None,
        max_tool_calls_per_request=5,
        log_level="INFO",
        tenant_id=TENANT,
        auth_audience=AUDIENCE,
        allowed_caller_app_ids=(ALLOWED_CALLER,),
    )


@pytest.fixture
def client(settings):
    app.dependency_overrides[get_settings] = lambda: settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def _token(key=SIGNING_KEY, **overrides) -> str:
    claims = {
        "aud": AUDIENCE,
        "iss": ISSUER,
        "exp": int(time.time()) + 300,
        "azp": ALLOWED_CALLER,
        "oid": "managed-identity-principal",
    }
    claims.update(overrides)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, key, algorithm="RS256")


def _chat(client, token):
    return client.post(
        "/v1/chat",
        json={"message": "Who is Pikachu?"},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_allowed_caller_reaches_the_route(client):
    # 501 means the auth check passed and the request reached the route.
    assert _chat(client, _token()).status_code == 501


def test_allowed_caller_identified_by_appid_claim(client):
    token = _token(azp=None, appid=ALLOWED_CALLER)
    assert _chat(client, token).status_code == 501


def test_wrong_audience_is_rejected(client):
    assert _chat(client, _token(aud="api://someone-else")).status_code == 401


def test_wrong_issuer_is_rejected(client):
    assert _chat(client, _token(iss="https://login.microsoftonline.com/other/v2.0")).status_code == 401


def test_expired_token_is_rejected(client):
    assert _chat(client, _token(exp=int(time.time()) - 60)).status_code == 401


def test_token_signed_by_another_key_is_rejected(client):
    assert _chat(client, _token(key=OTHER_KEY)).status_code == 401


def test_unsigned_token_is_rejected(client):
    unsigned = jwt.encode(
        {"aud": AUDIENCE, "iss": ISSUER, "exp": int(time.time()) + 300, "azp": ALLOWED_CALLER},
        key=None,
        algorithm="none",
    )
    assert _chat(client, unsigned).status_code == 401


def test_other_app_is_forbidden(client):
    assert _chat(client, _token(azp="22222222-2222-2222-2222-222222222222")).status_code == 403


def test_token_without_caller_claim_is_forbidden(client):
    assert _chat(client, _token(azp=None)).status_code == 403


def test_nothing_is_accepted_when_auth_is_not_configured(client, settings):
    app.dependency_overrides[get_settings] = lambda: Settings(
        key_vault_url=None,
        max_tool_calls_per_request=5,
        log_level="INFO",
        tenant_id=None,
        auth_audience=None,
        allowed_caller_app_ids=(),
    )
    assert _chat(client, _token()).status_code == 503


def test_settings_read_caller_list_from_env(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", TENANT)
    monkeypatch.setenv("AGENT_AUTH_AUDIENCE", AUDIENCE)
    monkeypatch.setenv("AGENT_ALLOWED_CALLER_APP_IDS", f" {ALLOWED_CALLER} , ,")
    loaded = Settings.from_env()
    assert loaded.allowed_caller_app_ids == (ALLOWED_CALLER,)
    assert loaded.auth_configured
