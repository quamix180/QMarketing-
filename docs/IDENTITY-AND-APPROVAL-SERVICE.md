# Identity and Human Approval Service

## Development implementation
The approval service now requires:
- a credential supplied by the authenticated caller;
- an injected `IdentityVerifier`;
- a verified principal with the `marketing_approver` role;
- a pending approval record;
- an exact match between the stored package digest and the supplied package;
- a single conditional database update so a concurrent second decision fails.

The service records approve/reject decisions and actor identity in the approval and audit tables. It does not send content to a platform.

## Production identity requirements
No identity provider is currently configured. Before production, implement and independently review an OIDC/JWT verifier that validates:
- cryptographic signature against trusted issuer keys;
- exact issuer and audience;
- expiry and not-before timestamps;
- key rotation and algorithm allowlist;
- subject and role claims from trusted identity administration;
- token revocation/session policy as applicable.

Never accept roles from a request body, agent output, untrusted metadata or user-controlled headers. Do not log bearer credentials. Protect the approval endpoint with TLS and CSRF protections appropriate to the chosen auth flow.

## Approval binding
Approval is single-use and bound to the persisted content ID, version, channel, destination account, action and canonical package SHA-256. Any modification requires a new content version and new approval request.

## Current limitation
The included verifier is an interface only; tests use a fake verifier. There is no HTTP endpoint, browser login, MFA, production identity provider or publisher. A successful unit test does not establish real user identity. Keep production publishing disabled until a real identity provider and end-to-end review flow pass security testing.
