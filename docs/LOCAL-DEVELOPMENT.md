# Local Development Guide

## Requirements
- Python 3.11 or later.
- No third-party Python packages are required for the current offline core.

## Run tests
From the repository root:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Use the SQLite development store

```python
from quamix_cmo.storage import CMOStore

store = CMOStore("./var/quamix-cmo-dev.sqlite3")
store.create_campaign("campaign-001", "QUAMIX", "Pilot", "Prepare an approval-ready content pilot")
store.create_content_item("content-001", "campaign-001", "text")
store.add_content_version(
    "content-001",
    1,
    "LinkedIn",
    {"text": "Internal draft only"},
    content_sha256="<sha256-of-canonical-content>",
    source_manifest=[],
)
```

The database creates tables and indexes from `src/quamix_cmo/schema.sql` on initialization. The sample is local development only; it does not create a human approval or publish anything.

## Current execution limits
- The orchestrator runs only injected agent adapters; no live model provider is configured.
- The approval table stores pending requests; authentication and a human approval UI are not yet implemented.
- No HTTP API, browser dashboard, social publisher or CRM connector is enabled.
- Do not put credentials, personal data or production records in the local development database.
- The SQLite schema is a development baseline, not a production migration strategy.

## Validation note
A successful test result must correspond to the exact branch commit being reviewed. The first 10-test GitHub Actions run predates the persistence and orchestrator work. Obtain and review a fresh CI run for the latest branch head before treating this slice as validated.
