"""Typed agent contracts and a no-network orchestration skeleton.

Concrete LLM/provider adapters are intentionally injected by the host application.
No agent receives publishing credentials or direct external-action tools.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    campaign_id: str
    brand_id: str
    objective: str
    approved_facts: tuple[dict[str, Any], ...] = ()
    channels: tuple[str, ...] = ("LinkedIn", "Instagram", "Facebook", "YouTube", "X", "TikTok")
    constraints: tuple[str, ...] = ("Draft only. Human approval required for external publication.",)


@dataclass(frozen=True)
class AgentResult:
    agent_name: str
    task_id: str
    status: str
    deliverable: dict[str, Any]
    sources: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    escalation_flags: tuple[str, ...] = ()


class CMOAgent(Protocol):
    name: str

    def run(self, task: AgentTask) -> AgentResult:
        """Return a structured result; implementations must not publish externally."""
        ...


@dataclass
class CMOOrchestrator:
    agents: dict[str, CMOAgent] = field(default_factory=dict)

    REQUIRED_AGENTS = (
        "Marketing Strategist",
        "Content Creation Director",
        "Social Media & Publishing Manager",
        "Community & Engagement Manager",
        "CRM & Lead Generation Manager",
        "Performance & Growth Analyst",
        "Marketing Automation & Integration Engineer",
    )

    def register(self, agent: CMOAgent) -> None:
        if agent.name not in self.REQUIRED_AGENTS:
            raise ValueError(f"unrecognized CMO agent: {agent.name}")
        if agent.name in self.agents:
            raise ValueError(f"agent already registered: {agent.name}")
        self.agents[agent.name] = agent

    def run_agent(self, agent_name: str, task: AgentTask) -> AgentResult:
        if agent_name not in self.REQUIRED_AGENTS:
            raise ValueError(f"unrecognized CMO agent: {agent_name}")
        if agent_name not in self.agents:
            raise RuntimeError(f"agent is not configured: {agent_name}")
        result = self.agents[agent_name].run(task)
        if result.task_id != task.task_id or result.agent_name != agent_name:
            raise ValueError("agent result identity does not match dispatched task")
        if result.status not in {"completed", "needs_review", "blocked", "failed"}:
            raise ValueError("agent returned an unsupported status")
        return result

    def readiness(self) -> dict[str, Any]:
        return {
            "required_agents": list(self.REQUIRED_AGENTS),
            "registered_agents": sorted(self.agents),
            "missing_agents": [name for name in self.REQUIRED_AGENTS if name not in self.agents],
            "ready_for_live_operation": False,
            "reason": "No production LLM adapters, identity service, approved tools or deployment are configured.",
        }
