# Agent change log: pokedex_agent_app

Each entry records one change made by an agent. Newest entries first.

| Date | Change | Reason | Files |
|---|---|---|---|
| 2026-11-22 | Added HTTP surface (`api.py`: `/healthz`, `/v1/chat` returns 501 until orchestration exists). Entry point now runs uvicorn on port 8000. Added FastAPI, uvicorn, pydantic, httpx dependencies. Replaced ci/deploy workflows with `ci-cd.yml` (dev on develop, itg on release/**). Added environment docs and architecture update. | Container App needs a listening process; release pattern | `src/pokedex_agent/api.py`, `main.py`, `pyproject.toml`, `Dockerfile`, `tests/test_api.py`, `.github/workflows/ci-cd.yml`, `docs/*` |
| 2026-11-21 | Created repository scaffold, configuration, tool client placeholder, container image, and CI/CD | Initial setup | All files |
| 2026-11-22 | Moved PokeAPI agent tool in-process: pokeapi.py (from pokedex_data_functions), new pokeapi_tool.py with TOOL_SPEC and run_tool(), OpenAPI spec moved to tools/specs as reference only, tests and docs updated; removed HTTP client build_url | Tool moved from data functions to agent | src/pokedex_agent/tools/*, tests/*, AGENTS.md, docs/*, README.md, SECURITY.md |
| 2026-11-21 | Renamed repository folder from ttaubes_pokedex_agent_app to pokedex_agent_app and updated references | Remove ttaubes_ prefix | All files |
