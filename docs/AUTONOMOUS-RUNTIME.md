# QUAMIX AI CMO — Autonomous Runtime

## Purpose

The runtime coordinates the seven specialist agents in a deterministic sequence and
passes each completed deliverable to the next agent as structured context. It is a
provider-neutral execution core: model adapters are injected by the future hosting
application, rather than embedding API keys or provider-specific code in this package.

## Execution order

1. Marketing Strategist
2. Content Creation Director
3. Social Media & Publishing Manager
4. Community & Engagement Manager
5. CRM & Lead Generation Manager
6. Performance & Growth Analyst
7. Marketing Automation & Integration Engineer

A run is marked `completed` only after all seven agents complete. If any agent returns
`needs_review`, `blocked`, or `failed`, the runtime stops and reports the stopping
agent. Missing agent configuration blocks the run before any agent is called.

## Safety boundary

The runtime has no publisher, outbound messaging, paid-ad, shell, or arbitrary external
tool interface. Agent constraints explicitly limit execution to drafting and analysis.
A completed run is not authorization to publish. Publication continues to require the
separate identity-verified approval service and exact content/package binding.

## Provider and deployment boundary

This package does not include a live LLM adapter, persistent job queue, web server,
OIDC implementation, social platform integration, or production scheduler. Those are
hosting-layer integrations and must be added and tested separately. Provider credentials
must be supplied through a secret manager or hosting environment, never committed to Git.

## Example integration

The hosting application should construct a `CMOOrchestrator`, register one concrete,
bounded adapter for each required agent, and call `AutonomousCMORuntime.run_campaign`.
The adapter contract is in `src/quamix_cmo/agents.py`. Adapters must not expose
publishing credentials or unrestricted tools to the agents.
