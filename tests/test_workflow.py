import unittest
from dataclasses import replace
from datetime import datetime, timezone

from quamix_cmo.approval import Approval, ApprovalGate, PublicationPackage
from quamix_cmo.workflow import ContentWorkflow, WorkflowError, transition


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.package = PublicationPackage(
            brand_id="QUAMIX", campaign_id="pilot", content_id="post", version=1,
            channel="LinkedIn", destination_account_id="org-1", action="publish",
            text="Draft", scheduled_at="2026-12-01T10:00:00+04:00",
        )
        self.gate = ApprovalGate({"founder"}, {"LinkedIn"})
        self.approval = Approval(
            approval_id="a1", approver_id="founder", decision="approved",
            package_digest=self.package.digest(), approved_at=datetime.now(timezone.utc).isoformat(),
            scope="single_package_publish",
        )
        self.awaiting = ContentWorkflow(self.package, status="AWAITING_APPROVAL", history=("IDEA", "AWAITING_APPROVAL"))

    def test_happy_path_stops_at_publish_handoff(self):
        approved = transition(self.awaiting, "APPROVED", gate=self.gate, approval=self.approval)
        scheduled = transition(approved, "SCHEDULED", gate=self.gate)
        ready = transition(scheduled, "READY_TO_PUBLISH", gate=self.gate)
        self.assertEqual(ready.status, "READY_TO_PUBLISH")
        self.assertEqual(ready.history[-3:], ("APPROVED", "SCHEDULED", "READY_TO_PUBLISH"))

    def test_cannot_approve_without_human_approval(self):
        with self.assertRaisesRegex(WorkflowError, "human approval"):
            transition(self.awaiting, "APPROVED")

    def test_cannot_skip_review(self):
        with self.assertRaisesRegex(WorkflowError, "invalid transition"):
            transition(ContentWorkflow(self.package), "APPROVED", gate=self.gate, approval=self.approval)

    def test_cannot_schedule_without_approval(self):
        approved = ContentWorkflow(self.package, status="APPROVED")
        with self.assertRaisesRegex(WorkflowError, "valid approval"):
            transition(approved, "SCHEDULED", gate=self.gate)

    def test_modified_package_fails_at_handoff(self):
        approved = transition(self.awaiting, "APPROVED", gate=self.gate, approval=self.approval)
        modified = replace(approved, package=replace(self.package, text="Changed"))
        with self.assertRaisesRegex(WorkflowError, "revalidation failed"):
            transition(modified, "SCHEDULED", gate=self.gate)

    def test_rejected_content_cannot_continue(self):
        rejected = transition(self.awaiting, "REJECTED")
        with self.assertRaisesRegex(WorkflowError, "invalid transition"):
            transition(rejected, "DRAFTED")


if __name__ == "__main__":
    unittest.main()
