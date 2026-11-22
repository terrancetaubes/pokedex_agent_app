"""Process entry point. Configures logging and starts the HTTP app."""

from __future__ import annotations

import logging

import uvicorn

from pokedex_agent.config import Settings


def main() -> None:
    settings = Settings.from_env()
    logging.basicConfig(level=settings.log_level)
    logging.getLogger(__name__).info(
        "Starting Pokedex agent. Max tool calls per request: %s",
        settings.max_tool_calls_per_request,
    )
    uvicorn.run("pokedex_agent.api:app", host="0.0.0.0", port=8000)
