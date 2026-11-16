import tempfile
import unittest
from pathlib import Path

from quamix_cmo.storage import CMOStore


class CMOStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CMOStore(Path(self.temp.name) / "cmo.sqlite3")
        self.store.create_campaign("camp-1", "QUAMIX", "Pilot", "Test draft workflow")

    def tearDown(self):
        self.temp.cleanup()

    def test_campaign_persists(self):
        self.assertEqual(self.store.get_campaign("camp-1")["brand_id"], "QUAMIX")

    def test_content_version_and_approval_persist(self):
        self.store.create_content_item("content-1", "camp-1")
        self.store.add_content_version(
            "content-1", 1, "LinkedIn", {"text": "Draft"},
            content_sha256="a" * 64, source_manifest=[{"ref": "approved-fact-1"}],
        )
        self.store.create_approval("approval-1", "content-1", 1, "LinkedIn", "page-1", "b" * 64)
        self.assertEqual(len(self.store.get_content_versions("content-1")), 1)
        self.assertEqual(self.store.get_approval("approval-1")["decision"], "pending")

    def test_lead_persists_with_evidence(self):
        self.store.record_lead(
            "lead-1", "contact-form", organization_name="Example Co",
            stated_interest="RWA data", qualification_score=40,
            qualification_evidence=[{"criterion": "stated_use_case", "evidence": "RWA data"}],
        )
        self.assertEqual(self.store.get_lead("lead-1")["qualification_score"], 40)

    def test_orphan_content_is_rejected(self):
        with self.assertRaises(Exception):
            self.store.create_content_item("orphan", "missing-campaign")

    def test_invalid_channel_is_rejected_by_database(self):
        self.store.create_content_item("content-2", "camp-1")
        with self.assertRaises(Exception):
            self.store.add_content_version(
                "content-2", 1, "UnknownPlatform", {"text": "Draft"},
                content_sha256="c" * 64,
            )

    def test_duplicate_version_channel_is_rejected(self):
        self.store.create_content_item("content-3", "camp-1")
        self.store.add_content_version(
            "content-3", 1, "LinkedIn", {"text": "Draft"},
            content_sha256="d" * 64,
        )
        with self.assertRaises(Exception):
            self.store.add_content_version(
                "content-3", 1, "LinkedIn", {"text": "Replacement"},
                content_sha256="e" * 64,
            )


if __name__ == "__main__":
    unittest.main()
