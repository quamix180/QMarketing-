"""Bounded, approval-safe execution runtime for the QUAMIX CMO agents.

The runtime coordinates registered agents in a fixed workflow, carries prior
agent deliverables forward as context, and stops on any non-completed result.
It deliberately has no publisher, outbound messaging, shell, or arbitrary tool
execution capability. Provider adapters are injected by the hosting service.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from uuid import uuid4

from .agents import AgentResult, AgentTask, CMOOrchestrator


@dataclass(frozen=True)
class AgentStep:
    agent_name: str
    status: str
    deliverable: dict[str, Any]


@dataclass(frozen=True)
class ExecutionReport:
    run_id: str
    task_id: str
    campaign_id: str
    status: str
    steps: tuple[AgentStep, ...]
    stop_reason: str | None = None

    @property
    def completed_agents(self) -> tuple[str, ...]:
        return tuple(step.agent_name for step in self.steps if step.status == "completed")


class AutonomousCMORuntime:
    """Execute a complete agent cycle, stopping safely when review is needed."""

    def __init__(self, orchestrator: CMOOrchestrator, *, max_context_bytes: int = 64_000):
        if max_context_bytes < 1024:
            raise ValueError("max_context_bytes must be at least 1024")
        self.orchestrator = orchestrator
        self.max_context_bytes = max_context_bytes

    def run_campaign(
        self,
        *,
        campaign_id: str,
        brand_id: str,
        objective: str,
        approved_facts: tuple[dict[str, Any], ...] = (),
        channels: tuple[str, ...] = ("LinkedIn", "Instagram", "Facebook", "YouTube", "X", "TikTok"),
    ) -> ExecutionReport:
        if not campaign_id.strip() or not brand_id.strip() or not objective.strip():
            raise ValueError("campaign_id, brand_id and objective are required")

        readiness = self.orchestrator.readiness()
        missing = readiness["missing_agents"]
        run_id = str(uuid4())
        task_id = str(uuid4())
        if missing:
            return ExecutionReport(
                run_id, task_id, campaign_id, "blocked", (),
                "Required agents are not configured: " + ", ".join(missing),
            )

        context: list[dict[str, Any]] = []
        steps: list[AgentStep] = []
        for agent_name in self.orchestrator.REQUIRED_AGENTS:
            task = AgentTask(
                task_id=task_id,
                campaign_id=campaign_id,
                brand_id=brand_id,
                objective=objective,
                approved_facts=tuple(approved_facts) + tuple(context),
                channels=channels,
                constraints=(
                    "Draft and analysis only.",
                    "No external publication, messaging, advertising spend or account changes.",
                    "Do not invent brand facts; identify assumptions and sources.",
                    "Human approval is required before any external publication.",
                ),
            )
            try:
                result: AgentResult = self.orchestrator.run_agent(agent_name, task)
                encoded = json.dumps(result.deliverable, sort_keys=True, separators=(",", ":"))
                if len(encoded.encode("utf-8")) > self.max_context_bytes:
                    return ExecutionReport(
                        run_id, task_id, campaign_id, "blocked", tuple(steps),
                        f"{agent_name} exceeded the configured deliverable size limit",
                    )
            except Exception as exc:
                # Do not expose provider exception contents, which may contain
                # request details or secrets, in the report.
                return ExecutionReport(
                    run_id, task_id, campaign_id, "failed", tuple(steps),
                    f"{agent_name} failed ({type(exc).__name__})",
                )

            steps.append(AgentStep(agent_name, result.status, result.deliverable))
            if result.status != "completed":
                return ExecutionReport(
                    run_id, task_id, campaign_id, "needs_review", tuple(steps),
                    f"{agent_name} returned status '{result.status}'",
                )
            context.append({"previous_agent": agent_name, "deliverable": result.deliverable})

        return ExecutionReport(run_id, task_id, campaign_id, "completed", tuple(steps))
