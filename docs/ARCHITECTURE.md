# Architecture

## Components

1. **Data pipeline** (`pokedex_data_functions`): Azure Functions. They extract data into ADLS Gen2. They expose no agent endpoints.
2. **Agent app** (this repository): Azure Container Apps, internal ingress. It hosts the agents and their tools.
3. **Backend** (`pokedex_backend`): Azure Container Apps, external ingress. It validates user tokens and calls the agent app.
4. **UI** (`pokedex_ui`): Azure Static Web Apps.
5. **Identity** (`pokedex_infra`): managed identities, RBAC, and CI identities.

## Tools

Tools run in-process, in `src/pokedex_agent/tools/`. The PokeAPI species tool calls `https://graphql.pokeapi.co/v1beta2` directly. Each tool exposes a `TOOL_SPEC` schema and a `run_tool()` function.

## Open decision: agent framework

Not chosen yet. Options: Microsoft Agent Framework or Semantic Kernel (Azure-supported, larger), plain Python with the model API (small, you build orchestration), or LangGraph (explicit graphs, another vendor). A human decides before the agent code is written.

## Caller authentication (implemented, not yet deployed)

`/v1/chat` requires a managed identity token. `src/pokedex_agent/auth.py` checks the signature (JWKS of the tenant), the issuer (v2), the audience (`AGENT_AUTH_AUDIENCE`), the expiry, and that the caller (`azp` or `appid`) is in `AGENT_ALLOWED_CALLER_APP_IDS`. If the settings are missing, every call gets 503.

It still needs an app registration `pokedex-agent` with an identifier URI `api://pokedex-agent`. The backend's `AGENT_APP_SCOPE` must match it. The app registration is not created yet. It belongs in `pokedex_infra/identity/entra.bicep`.
