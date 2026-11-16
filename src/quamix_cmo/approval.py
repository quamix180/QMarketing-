"""Fail-closed approval package validation. No network or publishing capability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Iterable


@dataclass(frozen=True)
class PublicationPackage:
    brand_id: str
    campaign_id: str
    content_id: str
    version: int
    channel: str
    destination_account_id: str
    action: str
    text: str
    media_sha256: tuple[str, ...] = ()
    links: tuple[str, ...] = ()
    scheduled_at: str = ""

    def digest(self) -> str:
        payload = {
            "brand_id": self.brand_id,
            "campaign_id": self.campaign_id,
            "content_id": self.content_id,
            "version": self.version,
            "channel": self.channel,
            "destination_account_id": self.destination_account_id,
            "action": self.action,
            "text": self.text,
            "media_sha256": list(self.media_sha256),
            "links": list(self.links),
            "scheduled_at": self.scheduled_at,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Approval:
    approval_id: str
    approver_id: str
    decision: str
    package_digest: str
    approved_at: str
    scope: str
    revoked: bool = False


class ApprovalError(ValueError):
    """Raised when an external-action approval check fails."""


class ApprovalGate:
    """Validates an approval record against the exact current package."""

    def __init__(self, authorized_approvers: Iterable[str], allowed_channels: Iterable[str]):
        self._approvers = frozenset(authorized_approvers)
        self._channels = frozenset(allowed_channels)

    def validate(self, package: PublicationPackage, approval: Approval) -> str:
        if not package.brand_id or not package.content_id or package.version < 1:
            raise ApprovalError("incomplete or invalid publication package")
        if package.channel not in self._channels:
            raise ApprovalError("channel is not allowlisted")
        if not package.destination_account_id:
            raise ApprovalError("destination account is missing")
        if package.action != "publish":
            raise ApprovalError("unsupported external action")
        if approval.approver_id not in self._approvers:
            raise ApprovalError("approver is not authorized")
        if approval.revoked:
            raise ApprovalError("approval has been revoked")
        if approval.decision != "approved":
            raise ApprovalError("publication has not been approved")
        if approval.scope != "single_package_publish":
            raise ApprovalError("approval scope is invalid")
        if approval.package_digest != package.digest():
            raise ApprovalError("approval does not match the exact package version")
        try:
            approved_at = datetime.fromisoformat(approval.approved_at.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise ApprovalError("approval timestamp is invalid") from exc
        if approved_at.tzinfo is None:
            raise ApprovalError("approval timestamp must include a timezone")
        if approved_at > datetime.now(timezone.utc):
            raise ApprovalError("approval timestamp is in the future")
        return package.digest()
