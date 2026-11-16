import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from quamix_cmo.approval import PublicationPackage
from quamix_cmo.approval_service import (
    ApprovalService, ApprovalServiceError, VerifiedPrincipal,
)
from quamix_cmo.storage import CMOStore


class StubVerifier:
    def __init__(self, principal=None, fail=False):
        self.principal = principal
        self.fail = fail

    def verify(self, credential):
        if self.fail or credential != "valid-test-credential":
            raise ValueError("invalid test credential")
        return self.principal


class ApprovalServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CMOStore(Path(self.temp.name) / "approval.sqlite3")
        self.store.create_campaign("camp", "QUAMIX", "Pilot", "Test")
        self.store.create_content_item("content", "camp")
        self.package = PublicationPackage(
            brand_id="QUAMIX", campaign_id="camp", content_id="content", version=1,
            channel="LinkedIn", destination_account_id="page-1", action="publish",
            text="Approved draft", scheduled_at="2026-12-01T10:00:00+04:00",
        )
        self.store.add_content_version(
            "content", 1, "LinkedIn", {"text": self.package.text},
            content_sha256=self.package.digest(),
        )
        self.store.create_approval(
            "approval", "content", 1, "LinkedIn", "page-1", self.package.digest(),
        )
        self.principal = VerifiedPrincipal("founder-123", frozenset({"marketing_approver"}))
        self.service = ApprovalService(self.store, StubVerifier(self.principal))

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_credential_approves_exact_package(self):
        self.service.decide("approval", self.package, "valid-test-credential")
        record = self.store.get_approval("approval")
        self.assertEqual(record["decision"], "approved")
        self.assertEqual(record["approver_subject"], "founder-123")

    def test_missing_credential_rejected(self):
        with self.assertRaisesRegex(ApprovalServiceError, "credential"):
            self.service.decide("approval", self.package, "")

    def test_unverified_identity_rejected(self):
        service = ApprovalService(self.store, StubVerifier(fail=True))
        with self.assertRaisesRegex(ApprovalServiceError, "verification failed"):
            service.decide("approval", self.package, "bad")

    def test_wrong_role_rejected(self):
        service = ApprovalService(
            self.store, StubVerifier(VerifiedPrincipal("user", frozenset({"viewer"})))
        )
        with self.assertRaisesRegex(ApprovalServiceError, "not authorized"):
            service.decide("approval", self.package, "valid-test-credential")

    def test_changed_text_cannot_be_approved(self):
        from dataclasses import replace
        changed = replace(self.package, text="Tampered after review")
        with self.assertRaisesRegex(ApprovalServiceError, "exact publication package"):
            self.service.decide("approval", changed, "valid-test-credential")

    def test_stored_content_version_digest_must_match(self):
        self.store.add_content_version(
            "content", 2, "LinkedIn", {"text": "different persisted version"},
            content_sha256="f" * 64,
        )
        from dataclasses import replace
        changed_package = replace(self.package, version=2)
        self.store.create_approval(
            "approval-v2", "content", 2, "LinkedIn", "page-1", changed_package.digest(),
        )
        with self.assertRaisesRegex(ApprovalServiceError, "persisted content version"):
            self.service.decide("approval-v2", changed_package, "valid-test-credential")

    def test_second_decision_is_rejected(self):
        self.service.decide("approval", self.package, "valid-test-credential")
        with self.assertRaisesRegex(ApprovalServiceError, "no longer pending"):
            self.service.decide("approval", self.package, "valid-test-credential")

    def test_unsupported_decision_rejected(self):
        with self.assertRaisesRegex(ApprovalServiceError, "must be approved or rejected"):
            self.service.decide("approval", self.package, "valid-test-credential", "publish")


if __name__ == "__main__":
    unittest.main()
