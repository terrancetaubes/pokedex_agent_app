"""HTTP surface for the agent app. Called by pokedex_backend only (internal ingress)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from pokedex_agent import __version__
from pokedex_agent.auth import require_caller

app = FastAPI(title="Pokedex agent", version=__version__)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatOut(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat", response_model=ChatOut)
def chat(body: ChatIn, caller: Annotated[dict, Depends(require_caller)]) -> ChatOut:
    # Agent orchestration is not built yet. Return 501 so callers see a clear state.
    raise HTTPException(status_code=501, detail="Agent orchestration is not implemented yet.")
