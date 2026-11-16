"""SQLite persistence for CMO campaign/content/approval/CRM records.

This module is a local development persistence layer. It does not provide
authentication, multi-tenant isolation, network access or production hardening.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CMOStore:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.executescript(schema)

    def create_campaign(self, campaign_id: str, brand_id: str, name: str, objective: str) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO campaigns
                   (campaign_id, brand_id, name, objective, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'IDEA', ?, ?)""",
                (campaign_id, brand_id, name, objective, now, now),
            )
            self._audit(connection, "system:local", "campaign.created", "campaign", campaign_id, {})

    def create_content_item(self, content_id: str, campaign_id: str, content_type: str = "text") -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO content_items
                   (content_id, campaign_id, content_type, status, current_version, created_at, updated_at)
                   VALUES (?, ?, ?, 'DRAFT', 1, ?, ?)""",
                (content_id, campaign_id, content_type, now, now),
            )
            self._audit(connection, "system:local", "content.created", "content", content_id, {})

    def add_content_version(
        self, content_id: str, version: int, channel: str, body: dict[str, Any],
        *, media_manifest: list[dict[str, Any]] | None = None,
        source_manifest: list[dict[str, Any]] | None = None, created_by: str = "system:local",
        content_sha256: str,
    ) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO content_versions
                   (content_id, version, channel, body_json, media_manifest_json,
                    source_manifest_json, content_sha256, created_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (content_id, version, channel, json.dumps(body, sort_keys=True),
                 json.dumps(media_manifest or [], sort_keys=True),
                 json.dumps(source_manifest or [], sort_keys=True),
                 content_sha256, created_by, now),
            )
            connection.execute(
                "UPDATE content_items SET current_version = ?, updated_at = ? WHERE content_id = ?",
                (version, now, content_id),
            )
            self._audit(connection, created_by, "content.version.created", "content", content_id,
                        {"version": version, "channel": channel})

    def create_approval(
        self, approval_id: str, content_id: str, version: int, channel: str,
        destination_account_id: str, package_sha256: str,
    ) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO approvals
                   (approval_id, content_id, version, channel, destination_account_id,
                    action, package_sha256, decision, created_at)
                   VALUES (?, ?, ?, ?, ?, 'publish', ?, 'pending', ?)""",
                (approval_id, content_id, version, channel, destination_account_id, package_sha256, now),
            )
            self._audit(connection, "system:local", "approval.requested", "approval", approval_id,
                        {"content_id": content_id, "version": version, "channel": channel})

    def record_lead(
        self, lead_id: str, source: str, pipeline_stage: str = "NEW",
        *, organization_name: str | None = None, contact_ref: str | None = None,
        stated_interest: str | None = None, sector: str | None = None,
        qualification_score: int | None = None,
        qualification_evidence: list[dict[str, Any]] | None = None,
        consent_id: str | None = None, owner_subject: str | None = None,
    ) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO leads
                   (lead_id, organization_name, contact_ref, source, stated_interest, sector,
                    qualification_score, qualification_evidence_json, consent_id, pipeline_stage,
                    owner_subject, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (lead_id, organization_name, contact_ref, source, stated_interest, sector,
                 qualification_score, json.dumps(qualification_evidence or [], sort_keys=True),
                 consent_id, pipeline_stage, owner_subject, now, now),
            )
            self._audit(connection, "system:local", "lead.recorded", "lead", lead_id,
                        {"source": source, "pipeline_stage": pipeline_stage})

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,)).fetchone()
            return dict(row) if row else None

    def get_content_versions(self, content_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM content_versions WHERE content_id = ? ORDER BY version, channel",
                (content_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM approvals WHERE approval_id = ?", (approval_id,)).fetchone()
            return dict(row) if row else None

    def get_lead(self, lead_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def _audit(connection: sqlite3.Connection, actor: str, event_type: str,
               object_type: str, object_id: str, details: dict[str, Any]) -> None:
        connection.execute(
            """INSERT INTO audit_events
               (event_id, actor_subject, event_type, object_type, object_id, details_json, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid4()), actor, event_type, object_type, object_id,
             json.dumps(details, sort_keys=True), utc_now()),
        )
