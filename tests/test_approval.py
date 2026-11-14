import unittest
from datetime import datetime, timezone, timedelta

from quamix_cmo.approval import Approval, ApprovalError, ApprovalGate, PublicationPackage


class ApprovalGateTests(unittest.TestCase):
    def setUp(self):
        self.package = PublicationPackage(
            brand_id="QUAMIX", campaign_id="pilot-001", content_id="post-001",
            version=1, channel="LinkedIn", destination_account_id="org-page-001",
            action="publish", text="Draft announcement", media_sha256=("a" * 64,),
            links=("https://example.invalid/",), scheduled_at="2026-12-01T10:00:00+04:00",
        )
        self.gate = ApprovalGate({"founder-approver"}, {"LinkedIn", "Instagram", "Facebook", "YouTube", "X", "TikTok"})
        self.approval = Approval(
            approval_id="approval-001", approver_id="founder-approver", decision="approved",
            package_digest=self.package.digest(), approved_at=datetime.now(timezone.utc).isoformat(),
            scope="single_package_publish",
        )

    def test_exact_approved_package_passes(self):
        self.assertEqual(self.gate.validate(self.package, self.approval), self.package.digest())

    def test_modified_text_invalidates_approval(self):
        changed = PublicationPackage(**{**self.package.__dict__, "text": "Changed after approval"})
        with self.assertRaisesRegex(ApprovalError, "exact package"):
            self.gate.validate(changed, self.approval)

    def test_modified_destination_invalidates_approval(self):
        changed = PublicationPackage(**{**self.package.__dict__, "destination_account_id": "other-page"})
        with self.assertRaises(ApprovalError):
            self.gate.validate(changed, self.approval)

    def test_unapproved_package_is_rejected(self):
        approval = Approval(**{**self.approval.__dict__, "decision": "pending"})
        with self.assertRaisesRegex(ApprovalError, "not been approved"):
            self.gate.validate(self.package, approval)

    def test_unauthorized_approver_is_rejected(self):
        approval = Approval(**{**self.approval.__dict__, "approver_id": "agent-copywriter"})
        with self.assertRaisesRegex(ApprovalError, "not authorized"):
            self.gate.validate(self.package, approval)

    def test_revoked_approval_is_rejected(self):
        approval = Approval(**{**self.approval.__dict__, "revoked": True})
        with self.assertRaisesRegex(ApprovalError, "revoked"):
            self.gate.validate(self.package, approval)

    def test_unallowlisted_channel_is_rejected(self):
        changed = PublicationPackage(**{**self.package.__dict__, "channel": "UnknownNetwork"})
        approval = Approval(**{**self.approval.__dict__, "package_digest": changed.digest()})
        with self.assertRaisesRegex(ApprovalError, "not allowlisted"):
            self.gate.validate(changed, approval)

    def test_future_approval_timestamp_is_rejected(self):
        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        approval = Approval(**{**self.approval.__dict__, "approved_at": future})
        with self.assertRaisesRegex(ApprovalError, "future"):
            self.gate.validate(self.package, approval)

    def test_timezone_is_required(self):
        approval = Approval(**{**self.approval.__dict__, "approved_at": "2026-11-15T12:00:00"})
        with self.assertRaisesRegex(ApprovalError, "timezone"):
            self.gate.validate(self.package, approval)

    def test_non_publish_action_is_rejected(self):
        changed = PublicationPackage(**{**self.package.__dict__, "action": "delete"})
        approval = Approval(**{**self.approval.__dict__, "package_digest": changed.digest()})
        with self.assertRaisesRegex(ApprovalError, "unsupported"):
            self.gate.validate(changed, approval)


if __name__ == "__main__":
    unittest.main()
