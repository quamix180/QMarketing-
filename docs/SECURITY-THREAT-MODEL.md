# Security and Privacy Threat Model

## Assets
Brand knowledge, unpublished campaigns, media assets, social account tokens, CRM/contact records, approval records, analytics, source code and audit logs.

## Trust boundaries
- Agent runtime vs deterministic policy and approval service.
- Draft content store vs immutable approved package.
- Approval dashboard/user identity vs publishing service.
- QUAMIX180 vs external social platforms and third-party providers.
- Marketing CRM data vs other QUAMIX departments and environments.

## Primary threats and controls
| Threat | Required control |
|---|---|
| Agent self-approves or fabricates approval | Independent authenticated approval service; model output is never authority |
| Content changes after approval | Canonical package digest; exact version/destination/action binding |
| Replay or duplicate publishing | One-time approval scope, idempotency key and provider receipt reconciliation |
| Wrong social account/channel | Destination allowlist and OAuth identity verification |
| Token leakage | Secrets manager, least privilege, redacted logs, rotation and revocation |
| Prompt injection via web pages/comments | Treat retrieved content as untrusted data; no policy/tool authority from content |
| False product or investment claims | Verified brand fact register, source provenance and human escalation |
| CRM misuse/spam | Inbound-first capture, consent/opt-out, purpose limitation and outbound approval |
| Data exposure between departments | Separate credentials, databases, storage and access scopes |
| Provider outage or ambiguous result | Fail closed; reconcile provider state before retry |
| Malicious/unsafe media | Asset provenance, rights review, malware scanning and controlled storage |
| Unauthorized production deployment | CI/staging gates, least-privilege deployment identity and Founder release approval |

## Data minimization
Collect only information needed for a stated business purpose. Store consent/source and retention metadata. Do not infer sensitive traits. Honor opt-outs and deletion requests. Restrict access to personal data and avoid sending CRM records to general-purpose model prompts unless an approved data-processing design permits it.

## Emergency controls
Provide a Founder-accessible global publishing pause, per-channel token revocation, queue stop, audit export and incident procedure. Kill switch must be enforced by the publisher, not merely displayed in a dashboard.

## Residual risk
This is a design-level threat model. No penetration test, deployment security review, provider assessment, privacy/legal review or production isolation test has been completed.
