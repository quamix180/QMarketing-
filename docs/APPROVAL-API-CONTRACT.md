# QUAMIX180 AI CMO — Approval API Contract

## Status

**Design contract only — not deployed and not yet backed by HTTP routes.** The current repository contains a provider-neutral approval service and SQLite development store. This document and `openapi/approval-api.yaml` define the next integration boundary without claiming that an API, dashboard, login flow or production identity provider exists.

## Scope

The future API supports only:
1. Listing approval records visible to the signed-in reviewer.
2. Reading the immutable content/media/source snapshot for review.
3. Recording an approve or reject decision against one exact package digest.

There is deliberately no publish, schedule, queue, social-platform or outbound-message endpoint. A successful approval response means only that the decision was recorded.

## Authentication and authorization

- Require HTTPS and an OIDC access token using the Authorization Bearer scheme.
- Validate signature, exact issuer and audience, expiry, not-before, algorithm allowlist, trusted key rotation and trusted role claims.
- Require the existing `marketing_approver` role for decision routes.
- Derive reviewer identity from the verified token subject. Never accept a subject or role from request JSON, query parameters, agent output or user-controlled headers.
- Enforce brand and destination-account scope on the server for every read and write. The current local data model does not yet implement multi-tenant authorization; production rollout is blocked until this is designed and tested.
- Do not log bearer tokens or other credentials. Apply rate limits, request-size limits, security headers and appropriate CSRF controls for the chosen browser authentication pattern.

## Decision integrity

A decision must match the persisted approval ID, content ID, version, channel, destination account, action and SHA-256 package digest. The API must not accept client-supplied content as the authoritative package. It loads the immutable package snapshot from trusted storage and compares the submitted digest.

Decisions are single-use. Concurrent approve/reject requests must produce at most one successful state transition. A stale or modified package requires a new content version and approval request. Use an idempotency key to make safe retries distinguishable from conflicting requests.

## Required HTTP behavior

See `openapi/approval-api.yaml` for the machine-readable contract:
- `GET /v1/approvals` — list only records visible to the reviewer.
- `GET /v1/approvals/{approvalId}` — retrieve the review snapshot.
- `POST /v1/approvals/{approvalId}/decision` — record approve/reject only.

Return non-disclosing 404 responses when a record is outside the caller's scope. Return 409 for already-decided or conflicting requests. Never turn an API approval into an implicit publishing action.

## Release gates before implementation can be exposed

- Select and configure the organization's OIDC provider; implement and independently review its verifier.
- Define trusted role administration and brand/account authorization mapping.
- Add tenant/brand scoping to persistence and prove isolation with negative tests.
- Add authenticated HTTP routes, schema validation, rate limiting, secure session handling and audit correlation.
- Build an authenticated reviewer UI that displays the exact content and media snapshot, destination account, source references and digest.
- Test forged roles, wrong issuer/audience, expired tokens, replay, stale digest, cross-brand access, revoked approvals, concurrent decisions and audit completeness.
- Complete security review and explicit Founder approval before staging exposure.

## Current safeguards

The existing `ApprovalService` uses an injected identity verifier and the `marketing_approver` role, checks the persisted package digest and uses a conditional single-use decision update. Its tests use a fake verifier. The current service has no HTTP listener, production identity provider, MFA, reviewer UI or publisher. SQLite remains local-development persistence only.
