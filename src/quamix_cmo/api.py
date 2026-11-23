"""Minimal authenticated HTTP host for the QUAMIX AI CMO draft-only core."""
from __future__ import annotations

import os
import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .agents import CMOOrchestrator
from .runtime import AutonomousCMORuntime
from .llm_agents import AGENT_INSTRUCTIONS, build_agents_from_environment

app = FastAPI(title="QUAMIX AI CMO Core", version="0.1.0", docs_url=None, redoc_url=None)

class CampaignRunRequest(BaseModel):
    campaign_id: str = Field(min_length=1, max_length=120)
    brand_id: str = Field(default="QUAMIX", min_length=1, max_length=80)
    objective: str = Field(min_length=5, max_length=4000)
    approved_facts: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    channels: list[str] = Field(default_factory=lambda: ["LinkedIn", "Instagram", "Facebook", "YouTube", "X", "TikTok"], max_length=12)


def _build_orchestrator() -> CMOOrchestrator:
    orchestrator = CMOOrchestrator()
    for agent in build_agents_from_environment():
        orchestrator.register(agent)
    return orchestrator

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "quamix-ai-cmo-core"}

@app.get("/readiness")
def readiness() -> dict[str, Any]:
    orchestrator = _build_orchestrator()
    result = orchestrator.readiness()
    result["api_auth_configured"] = bool(os.getenv("CMO_API_TOKEN"))
    result["llm_provider_configured"] = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_MODEL"))
    result["execution_enabled"] = result["api_auth_configured"] and result["llm_provider_configured"] and not result["missing_agents"]
    result["external_actions_enabled"] = False
    result["publication_requires_human_approval"] = True
    return result

@app.post("/campaigns/run")
def run_campaign(request: CampaignRunRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    expected = os.getenv("CMO_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="CMO API authentication is not configured")
    if not authorization or not authorization.startswith("Bearer ") or not secrets.compare_digest(authorization[7:], expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_MODEL"):
        raise HTTPException(status_code=503, detail="LLM provider is not configured")
    orchestrator = _build_orchestrator()
    report = AutonomousCMORuntime(orchestrator).run_campaign(
        campaign_id=request.campaign_id,
        brand_id=request.brand_id,
        objective=request.objective,
        approved_facts=tuple(request.approved_facts),
        channels=tuple(request.channels),
    )
    return {
        "run_id": report.run_id,
        "task_id": report.task_id,
        "campaign_id": report.campaign_id,
        "status": report.status,
        "completed_agents": list(report.completed_agents),
        "steps": [{"agent_name": step.agent_name, "status": step.status, "deliverable": step.deliverable} for step in report.steps],
        "stop_reason": report.stop_reason,
        "external_actions_enabled": False,
    }
