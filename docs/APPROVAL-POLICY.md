# Approval and External-Action Policy

## Current policy: approval required
Every external publication or communication requires an authorized human approval. This includes social posts, comments/replies, direct messages, newsletter sends, website articles and partner outreach.

## Actions agents may perform independently
- Internal research and strategy proposals using permitted sources.
- Internal content drafts and creative asset drafts.
- Channel-specific adaptations and metadata drafts.
- Internal factual/brand/copyright/privacy checks.
- Internal CRM classification of authorized inbound leads.
- Internal analytics and recommendations from real connected data.
- Submit a complete package to the approval queue.

## Actions that are blocked until separate authorization
- Publishing or scheduling public content.
- Public comment replies or direct messages.
- Newsletter or bulk email sends.
- Paid advertising, boosting or budget changes.
- CRM outbound sequences or prospect contact.
- Pricing, product, investment, regulatory or legal commitments.
- Sharing confidential information or personal data externally.
- Production deployment, credential administration or spending.

## Approval package
An approval must bind:
- brand ID, campaign ID, content ID and immutable version;
- platform, destination account and publication action;
- exact text, links, hashtags, alt text and metadata;
- media asset identifiers and cryptographic digests;
- scheduled time/timezone;
- approver identity, role, timestamp and decision;
- applicable policy/version and review evidence.

Any change to the package invalidates approval. Approval is single-purpose and cannot be reused for another account, channel, time or action.

## Publisher enforcement
The publisher must independently verify:
1. authenticated approver is authorized for this action;
2. approval is approved, current and not revoked;
3. current package digest exactly matches the approved digest;
4. channel/account is on the allowlist and authorized;
5. scheduled action is within approval scope and time window;
6. idempotency key has not already been consumed;
7. policy service and audit store are available.

If any check fails, stop without external side effects. A model's statement that something is approved is never sufficient.

## Escalation
Human review is mandatory for investment/financial claims, regulatory or legal matters, security incidents, complaints, reputational crises, sensitive personal data, customer commitments, fundraising, partnerships and paid campaigns.

## Audit
Record every draft version, agent run, review result, approval decision, attempted external action, provider response and failure. Never log secrets or unnecessary personal data.
