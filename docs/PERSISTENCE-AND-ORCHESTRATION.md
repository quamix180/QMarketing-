# Persistence and Agent Orchestration — Development Slice

## Included in this slice
- SQLite schema for campaigns, content items, immutable channel versions, pending approvals, audit events, consent records and inbound leads.
- A local SQLite repository with parameterized SQL and foreign-key constraints.
- Typed agent task/result contracts for the seven specialist roles.
- An injectable orchestrator that validates agent registration and result identity.
- Tests for campaign/content/approval/lead persistence and agent contract behavior.

## Explicit limitations
- SQLite is a local development database, not a production multi-user deployment.
- The current approval persistence method creates pending approval requests only; it does not authenticate a human or approve publication.
- No API server, web dashboard, authentication provider, LLM adapter, model key, social account, CRM connector or publisher is included.
- The seven agents are interfaces only. A stub agent in tests demonstrates the contract; no live AI agents are claimed.
- Production requires PostgreSQL or another approved shared database, migrations, tenant/access controls, authenticated approval identity, encryption, backups, audit integrity and operational monitoring.

## Next engineering step
Build a secure authenticated API and review dashboard against these repository interfaces. Keep every channel action in draft-only mode until human identity, exact-package approval and official platform API authorization are tested end-to-end.
