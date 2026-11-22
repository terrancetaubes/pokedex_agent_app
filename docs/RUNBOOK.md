# Runbook

## CI fails

Run `ruff check .` and `pytest` locally from the repository root. Fix the reported issue.

## Container App revision fails to start

1. Open the revision's logs in the Container App blade or Log Analytics.
2. Check that the image exists in ACR with the tag of the commit.
3. Check that `AZURE_CLIENT_ID` on the container matches the agent managed identity.

## Roll back

Set the Container App to a previous image: `az containerapp update --name <app> --resource-group <rg> --image <acr>.azurecr.io/pokedex-agent:<previous-sha>`. Then revert the commit on the branch.
