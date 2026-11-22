from fastapi.testclient import TestClient

from pokedex_agent.api import app


def test_healthz():
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok"}


def test_chat_is_not_implemented_yet():
    client = TestClient(app)
    response = client.post("/v1/chat", json={"message": "Who is Pikachu?"})
    assert response.status_code == 501


def test_chat_rejects_empty_message():
    client = TestClient(app)
    assert client.post("/v1/chat", json={"message": ""}).status_code == 422
