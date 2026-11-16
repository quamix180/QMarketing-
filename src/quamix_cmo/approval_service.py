"""Human approval service with an injected trusted identity verifier.

No concrete identity provider is included. Production callers must inject an
OIDC/JWT verifier that validates signature, issuer, audience, expiry and roles.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from .approval import Approval, ApprovalGate, PublicationPackage
from .storage import CMOStore


@dataclass(frozen=True)
class VerifiedPrincipal:
    subject: str
    roles: frozenset[str]


class IdentityVerifier(Protocol):
    def verify(self, credential: str) -> VerifiedPrincipal:
        """Verify credential cryptographically and return trusted identity claims."""
        ...


class ApprovalServiceError(ValueError):
    pass


class ApprovalService:
    def __init__(
        self,
        store: CMOStore,
        identity_verifier: IdentityVerifier,
        allowed_channels: tuple[str, ...] = ("LinkedIn", "Instagram", "Facebook", "YouTube", "X", "TikTok"),
        required_role: str = "marketing_approver",
    ):
        self.store = store
        self.identity_verifier = identity_verifier
        self.allowed_channels = allowed_channels
        self.required_role = required_role

    def decide(
        self, approval_id: str, package: PublicationPackage, credential: str, decision: str = "approved"
    ) -> None:
        if decision not in {"approved", "rejected"}:
            raise ApprovalServiceError("decision must be approved or rejected")
        if not credential:
            raise ApprovalServiceError("authenticated credential is required")
        try:
            principal = self.identity_verifier.verify(credential)
        except Exception as exc:
            raise ApprovalServiceError("identity verification failed") from exc
        if not isinstance(principal, VerifiedPrincipal) or not principal.subject:
            raise ApprovalServiceError("identity verifier returned no trusted principal")
        if self.required_role not in principal.roles:
            raise ApprovalServiceError("principal is not authorized to approve marketing content")

        record = self.store.get_approval(approval_id)
        if record is None:
            raise ApprovalServiceError("approval request does not exist")
        if record["decision"] != "pending":
            raise ApprovalServiceError("approval request is no longer pending")
        stored_version = self.store.get_content_version(
            package.content_id, package.version, package.channel
        )
        if stored_version is None or stored_version["content_sha256"] != package.digest():
            raise ApprovalServiceError("publication package does not match the persisted content version")
        if (
            record["content_id"] != package.content_id
            or record["version"] != package.version
            or record["channel"] != package.channel
            or record["destination_account_id"] != package.destination_account_id
            or record["action"] != package.action
            or record["package_sha256"] != package.digest()
        ):
            raise ApprovalServiceError("approval request does not match the exact publication package")

        approved_at = datetime.now(timezone.utc).isoformat()
        approval = Approval(
            approval_id=approval_id,
            approver_id=principal.subject,
            decision=decision,
            package_digest=record["package_sha256"],
            approved_at=approved_at,
            scope="single_package_publish",
        )
        # The publication gate validates permission to publish, so it applies
        # only to an approval decision. A rejection still requires the exact
        # persisted package binding above, but must remain possible for a
        # reviewer who is preventing publication.
        if decision == "approved":
            gate = ApprovalGate({principal.subject}, self.allowed_channels)
            try:
                gate.validate(package, approval)
            except ValueError as exc:
                raise ApprovalServiceError(f"approval policy rejected request: {exc}") from exc

        if not self.store.decide_approval(approval_id, decision, principal.subject):
            raise ApprovalServiceError("approval request was already decided by another reviewer")
