PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL,
    name TEXT NOT NULL,
    objective TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('IDEA','RESEARCH','PLANNED','ACTIVE','PAUSED','COMPLETED','CANCELLED')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_items (
    content_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    content_type TEXT NOT NULL CHECK (content_type IN ('text','image','carousel','audio','video','article')),
    status TEXT NOT NULL CHECK (status IN ('DRAFT','IN_REVIEW','APPROVED','REJECTED','ARCHIVED')),
    current_version INTEGER NOT NULL CHECK (current_version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_versions (
    content_id TEXT NOT NULL REFERENCES content_items(content_id),
    version INTEGER NOT NULL CHECK (version >= 1),
    channel TEXT NOT NULL CHECK (channel IN ('LinkedIn','Instagram','Facebook','YouTube','X','TikTok','QUAMIX.News')),
    body_json TEXT NOT NULL,
    media_manifest_json TEXT NOT NULL DEFAULT '[]',
    source_manifest_json TEXT NOT NULL DEFAULT '[]',
    content_sha256 TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (content_id, version, channel)
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    channel TEXT NOT NULL,
    destination_account_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action = 'publish'),
    package_sha256 TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('pending','approved','rejected','revoked')),
    approver_subject TEXT,
    decided_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (content_id, version, channel)
      REFERENCES content_versions(content_id, version, channel)
);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    actor_subject TEXT NOT NULL,
    event_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consent_records (
    consent_id TEXT PRIMARY KEY,
    subject_ref TEXT NOT NULL,
    purpose TEXT NOT NULL,
    source TEXT NOT NULL,
    lawful_basis TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active','withdrawn','expired','unknown')),
    captured_at TEXT NOT NULL,
    expires_at TEXT,
    evidence_ref TEXT
);

CREATE TABLE IF NOT EXISTS leads (
    lead_id TEXT PRIMARY KEY,
    organization_name TEXT,
    contact_ref TEXT,
    source TEXT NOT NULL,
    stated_interest TEXT,
    sector TEXT,
    qualification_score INTEGER CHECK (qualification_score BETWEEN 0 AND 100),
    qualification_evidence_json TEXT NOT NULL DEFAULT '[]',
    consent_id TEXT REFERENCES consent_records(consent_id),
    pipeline_stage TEXT NOT NULL CHECK (pipeline_stage IN ('NEW','QUALIFIED','CONTACTED','ENGAGED','MEETING','PROPOSAL','NEGOTIATION','WON','LOST','NURTURE')),
    owner_subject TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_content_campaign ON content_items(campaign_id);
CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status);
CREATE INDEX IF NOT EXISTS idx_approvals_decision ON approvals(decision);
CREATE INDEX IF NOT EXISTS idx_leads_stage ON leads(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_audit_object ON audit_events(object_type, object_id);
