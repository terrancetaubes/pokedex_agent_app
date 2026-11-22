# Environments

Branch-to-environment mapping: `../../docs/BRANCHING_AND_RELEASE.md` in the project folder.

## GitHub environment variables (set in `dev` and `itg`)

| Name | Type | Value |
|---|---|---|
| `AZURE_TENANT_ID` | variable | Tenant ID |
| `AZURE_SUBSCRIPTION_ID` | variable | Subscription ID |
| `AZURE_CLIENT_ID` | variable | `gh-pokedex-agent-app-<env>` client ID |
| `AZURE_RESOURCE_GROUP` | variable | `rg-pokedex-<env>` |
| `AZURE_ACR_NAME` | variable | `crpokedex<env><suffix>` |
| `AZURE_CONTAINERAPP_NAME` | variable | `ca-agent-pokedex-<env>` |
| `POKEDEX_MAX_TOOL_CALLS` | variable | Integer from 1 to 20. Suggested start: 5 |
| `AGENT_AUTH_AUDIENCE` | variable | Audience of this app's token, `api://pokedex-agent` (set when the app registration exists) |
| `AGENT_ALLOWED_CALLER_APP_IDS` | variable | Comma-separated client IDs of the managed identities allowed to call. The backend identity (`gh-pokedex-backend-<env>`, or the managed identity client ID) |

Names come from `pokedex_infra/docs/ENVIRONMENTS.md`.

If `AZURE_TENANT_ID`, `AGENT_AUTH_AUDIENCE`, or `AGENT_ALLOWED_CALLER_APP_IDS` is missing, `/v1/chat` returns 503 for every call. The app does not start open.

## Runtime

- The container listens on port 8000.
- Ingress is internal. Only `pokedex_backend` can call it.
- The container uses the agent managed identity. Its only roles are AcrPull and Key Vault Secrets User.
