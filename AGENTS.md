# AGENTS.md: pokedex_agent_app

Read the parent `../AGENTS.md` first. Its rules apply here.

## Purpose

A multi-agent application that answers Pokedex questions. Agents call the data services in `pokedex_data_functions` as tools. The app runs in Azure Container Apps and uses a user-assigned managed identity.

## Layout

| Path | Contents |
|---|---|
| `src/pokedex_agent/config.py` | Settings from environment variables. No secrets in code. |
| `src/pokedex_agent/main.py` | Entry point |
| `src/pokedex_agent/agents/` | Agent definitions and orchestration (placeholder) |
| `src/pokedex_agent/tools/pokeapi_tool.py` | PokeAPI species-traits tool: `TOOL_SPEC` (agent-facing schema) and `run_tool()` |
| `src/pokedex_agent/tools/pokeapi.py` | PokeAPI GraphQL client (moved from `pokedex_data_functions`) |
| `src/pokedex_agent/tools/specs/` | Former OpenAPI spec, reference only. Its server URL is obsolete. |
| `tests/` | pytest tests. Unit tests must not call Azure. |
| `Dockerfile` | Container image for Container Apps |
| `.github/workflows/ci.yml` | Lint and tests on every pull request |
| `.github/workflows/deploy.yml` | Build image in ACR, then update the Container App |

## Rules for agents

- Tools run in-process. Define each tool's schema in `TOOL_SPEC` and keep it in step with the function signature. Do not invent tools or endpoints.
- Tools return result dicts with `ok` and `error` or `data`. They must not raise for expected failures, and must not return raw exception text to the agent.
- Authenticate to Azure with `DefaultAzureCredential`. Do not add keys, tokens, or connection strings.
- Read secrets from Key Vault through the managed identity. Never store them in `.env` files in the repository.
- Every agent must have a limit on tool calls per request. Add the limit in `config.py` and test it.
- Every agent response that uses tool output must include the source of that output.
- Add tests for every new tool. Run `ruff check` and `pytest` before you finish.
- Log every change in `AGENT_CHANGELOG.md`.

## Open decisions

- The agent framework is not chosen yet. Options and trade-offs are in `docs/ARCHITECTURE.md`. Do not add a framework dependency without a human decision.
