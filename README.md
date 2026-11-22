# pokedex_agent_app

Multi-agent Pokedex application for Azure Container Apps. Agents use the Pokedex data services as tools.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest
python -m pokedex_agent
```

Copy `.env.example` to `.env` for local settings. Never commit `.env`.

## CI/CD

- Pull requests and pushes to `develop` or `release/**`: lint and tests (`ci-cd.yml`).
- Merge to `develop`: build the image in ACR and deploy to `dev`.
- Push to `release/<n>`: build the image in ACR and deploy to `itg`.

Branch flow: `docs/BRANCHING_AND_RELEASE.md` in the project folder. Environment settings: `docs/ENVIRONMENTS.md`.

Tools live in `src/pokedex_agent/tools/`. See `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`, and `SECURITY.md`.
