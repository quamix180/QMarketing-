# QUAMIX180 AI CMO

Approval-gated autonomous marketing operations for the QUAMIX brand.

## Current stage

The repository contains a tested workflow and governance foundation, an identity-gated
approval service contract, and a provider-neutral autonomous agent runtime. The runtime
coordinates seven specialist agents and stops safely when a specialist needs review.
It is not yet a deployed application or a live autonomous service.

## Confirmed operating decisions

- Brand: QUAMIX.
- Channels: LinkedIn, Instagram, Facebook, YouTube, X and TikTok.
- Autonomy: AI agents may research, plan, draft, create assets, review, coordinate and
  analyze. External publication requires a human approval record.
- Public publishing, paid advertising, outbound prospect messaging, CRM communications
  and production deployment remain disabled until separately authorized and verified.

## Repository map

- `docs/`: charter, architecture, governance, integrations, CRM, KPI model, roadmap and runtime.
- `src/quamix_cmo/`: deterministic workflow, approval-gate core and autonomous runtime.
- `tests/`: offline tests; no live social API calls.
- `.github/workflows/`: CI checks.

## Safety invariant

The publishing boundary must fail closed. No publication may proceed without a valid
approval record bound to the exact content version, media digests, destination account,
channel and scheduled action. Changes invalidate prior approval. The autonomous runtime
does not contain publishing capabilities.

## Development

The core uses Python's standard library.

Run tests:

```sh
python -m unittest discover -s tests -v
```

See [the implementation plan](docs/IMPLEMENTATION-PLAN.md),
[approval policy](docs/APPROVAL-POLICY.md), and
[autonomous runtime](docs/AUTONOMOUS-RUNTIME.md).
