# Technical Architecture

## Logical services
- **CMO orchestrator:** owns campaign/task state and dispatches bounded work.
- **Agent runtime:** invokes specialist agents with least-privilege tools and explicit input/output schemas.
- **Brand knowledge service:** retrieves approved facts with source, owner, review date and status.
- **Content service:** stores campaign briefs, content versions, channel variants and asset references.
- **Creative service:** generates/assembles images, audio and video; records model/tool provenance and usage rights.
- **Review service:** runs deterministic and assisted checks; reviewer is separate from generator.
- **Approval service:** records approver, decision, exact package digest and scope.
- **Publisher:** isolated service that accepts only approved package IDs and revalidates approval immediately before the external API call.
- **CRM/community service:** stores authorized inbound interactions, consent and follow-up tasks.
- **Analytics service:** ingests platform/website/CRM metrics with source and freshness metadata.

## Suggested technology choices (not yet connected)
- Python/FastAPI for application APIs.
- PostgreSQL for campaigns, versions, approvals, CRM references and audit events.
- Object storage for creative assets.
- Background queue for long-running jobs.
- Web approval dashboard.
- Secrets manager for OAuth/API tokens.
- OpenTelemetry-compatible logs/metrics and alerting.
- n8n may orchestrate external workflows if its deployment, permissions and data handling pass review. Avoid duplicate infrastructure where QUAMIX already has an approved equivalent.

## Data entities
brands, brand_facts, brand_sources, audiences, campaigns, campaign_briefs, content_items, content_versions, media_assets, agent_runs, review_results, approvals, social_accounts, publish_jobs, publish_events, inbound_interactions, consent_records, leads, crm_events, analytics_snapshots, audit_events.

## Security boundaries
- Agents cannot read secrets or call publisher credentials.
- Publisher has no ability to create or modify content.
- Approval service is independent of model output.
- Platform credentials are scoped per channel/account and revocable.
- No production database, unrelated departmental repository or private customer data is mounted into an agent.
- All external actions are allowlisted, logged and idempotent where possible.
- Fail closed on unavailable policy, identity, approval or destination checks.

## Deployment topology
Development -> automated tests -> isolated staging -> Founder-approved production release. Separate identities, databases, queues, storage, secrets and logs by environment. No direct deployment from a model-generated branch to production.
