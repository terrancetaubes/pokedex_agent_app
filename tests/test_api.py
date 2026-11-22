import pytest
from fastapi.testclient import TestClient

from pokedex_agent.api import app
from pokedex_agent.auth import get_settings, require_caller
from pokedex_agent.config import Settings


def _settings(configured: bool = True) -> Settings:
    return Settings(
        key_vault_url=None,
        max_tool_calls_per_request=5,
        log_level="INFO",
        tenant_id="00000000-0000-0000-0000-000000000000" if configured else None,
        auth_audience="api://pokedex-agent" if configured else None,
        allowed_caller_app_ids=("11111111-1111-1111-1111-111111111111",) if configured else (),
    )


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


def test_healthz_is_public():
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok"}


def test_chat_requires_a_caller_token():
    app.dependency_overrides[get_settings] = _settings
    client = TestClient(app)
    response = client.post("/v1/chat", json={"message": "Who is Pikachu?"})
    assert response.status_code == 401


def test_chat_refuses_everything_when_auth_is_not_configured():
    app.dependency_overrides[get_settings] = lambda: _settings(configured=False)
    client = TestClient(app)
    response = client.post(
        "/v1/chat",
        json={"message": "Who is Pikachu?"},
        headers={"Authorization": "Bearer anything"},
    )
    assert response.status_code == 503


def test_chat_with_verified_caller_is_not_implemented_yet():
    app.dependency_overrides[require_caller] = lambda: {"azp": "11111111-1111-1111-1111-111111111111"}
    client = TestClient(app)
    response = client.post("/v1/chat", json={"message": "Who is Pikachu?"})
    assert response.status_code == 501


def test_chat_rejects_empty_message():
    app.dependency_overrides[require_caller] = lambda: {"azp": "11111111-1111-1111-1111-111111111111"}
    client = TestClient(app)
    assert client.post("/v1/chat", json={"message": ""}).status_code == 422
