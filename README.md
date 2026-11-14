# QUAMIX180 AI CMO

Approval-gated marketing automation for the QUAMIX brand.

## Current stage

This repository is being initialized as the development home for the QUAMIX180 AI CMO. The first implementation is deliberately non-publishing: it will establish the brand/agent specification, content workflow, approval controls, tests and integration contracts before any live social account is connected.

## Confirmed operating decisions

- Brand: QUAMIX.
- Channels: LinkedIn, Instagram, Facebook, YouTube, X and TikTok.
- Autonomy: AI may research, plan, draft, create assets, review and prepare posts; a human approver must authorize every external publication.
- Public publishing, paid advertising, outbound prospect messaging, CRM communications and production deployment remain disabled until separately authorized and technically verified.

## Repository map

- `docs/`: charter, architecture, governance, integrations, CRM, KPI model and roadmap.
- `src/quamix_cmo/`: deterministic workflow and approval-gate core.
- `tests/`: offline tests; no live social API calls.
- `.github/workflows/`: CI checks.

## Safety invariant

The publishing boundary must fail closed. No publication may proceed without a valid approval record bound to the exact content version, media digests, destination account, channel and scheduled action. Changes invalidate prior approval. This repository does not contain platform credentials and does not enable live publishing.

## Development

The initial core uses Python's standard library so the safety model can be tested without paid services or external credentials.

Run tests:

```sh
python -m unittest discover -s tests -v
```

See [the implementation plan](docs/IMPLEMENTATION-PLAN.md) and [approval policy](docs/APPROVAL-POLICY.md).
