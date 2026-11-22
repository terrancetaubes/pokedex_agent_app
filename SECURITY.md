# Security policy

## Reporting a vulnerability

Do not open a public issue. Contact the repository owner directly through a private channel.

## Rules

- No secrets in code, `.env` files, images, or workflow files.
- The app authenticates to Azure with its user-assigned managed identity. Its role is `AcrPull`, `Key Vault Secrets User`, and read or write on the data lake (see `pokedex_infra/identity/rbac.bicep`).
- Agents may call only the tools listed in `src/pokedex_agent/tools/`.
- The PokeAPI tool sends a species ID only. It sends no user data and no Azure credentials.
- Treat all model output and all tool output as untrusted input when it reaches a shell, a query, or a URL.
- Pull requests from forks do not receive Azure credentials.
