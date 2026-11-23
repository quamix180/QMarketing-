"""OpenAI-compatible, draft-only agent adapters for the QUAMIX CMO core."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any

from .agents import AgentResult, AgentTask

AGENT_INSTRUCTIONS: dict[str, str] = {
    "Marketing Strategist": "Develop positioning, audience, campaign objectives, strategy, risks and measurable goals.",
    "Content Creation Director": "Create an editorial plan and draft content concepts, outlines and copy. Include fact-checking notes and sources needed.",
    "Social Media & Publishing Manager": "Adapt draft content for the requested channels. Prepare posting recommendations and platform-specific copy; do not publish.",
    "Community & Engagement Manager": "Prepare community engagement ideas, responses and moderation guidance. Do not contact anyone.",
    "CRM & Lead Generation Manager": "Identify institutional prospecting approaches and qualification criteria. Do not collect sensitive personal data or contact prospects.",
    "Performance & Growth Analyst": "Define KPIs, measurement plan, hypotheses and optimization recommendations. Clearly distinguish estimates from facts.",
    "Marketing Automation & Integration Engineer": "Recommend workflow automation, technical integration steps, data requirements and safeguards. Do not execute integrations or change accounts.",
}

class OpenAIAgent:
    def __init__(self, name: str, model: str, api_key: str, timeout_seconds: int = 90):
        if name not in AGENT_INSTRUCTIONS:
            raise ValueError("unknown agent")
        self.name, self.model, self.api_key = name, model, api_key
        self.timeout_seconds = timeout_seconds

    def run(self, task: AgentTask) -> AgentResult:
        prompt = {
            "role": self.name,
            "instructions": AGENT_INSTRUCTIONS[self.name],
            "objective": task.objective,
            "brand_id": task.brand_id,
            "campaign_id": task.campaign_id,
            "channels": list(task.channels),
            "approved_facts_and_prior_context": list(task.approved_facts),
            "constraints": list(task.constraints),
            "output_schema": {
                "summary": "string",
                "recommendations": "array of strings",
                "drafts_or_work_products": "array of objects or strings",
                "assumptions": "array of strings",
                "sources_to_verify": "array of strings",
                "risks_or_review_flags": "array of strings"
            },
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a QUAMIX marketing specialist. Return only a valid JSON object matching the requested output schema. Do not invent facts. Mark unverified statements as assumptions. You may research only from supplied context; list sources that must be verified. Draft and analysis only: never publish, message, spend money, change accounts, or claim actions were executed."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
            content = raw["choices"][0]["message"]["content"]
            deliverable: dict[str, Any] = json.loads(content)
            if not isinstance(deliverable, dict):
                raise ValueError("response must be a JSON object")
            return AgentResult(self.name, task.task_id, "completed", deliverable)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            # Deliberately avoid returning provider request/response content or secrets.
            raise RuntimeError(type(exc).__name__) from None


def build_agents_from_environment() -> list[OpenAIAgent]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not api_key or not model:
        return []
    return [OpenAIAgent(name, model, api_key) for name in AGENT_INSTRUCTIONS]
