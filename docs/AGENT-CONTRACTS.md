# Seven AI Agent Contracts

All agents are advisory workers invoked by the QUAMIX180 orchestrator. They receive only the minimum campaign context and approved knowledge required for their task. They cannot grant themselves permissions, approve content, read secrets or directly perform external actions.

## Shared input contract
- task_id, campaign_id, brand_id;
- task objective and requested deliverable;
- approved brand facts and source references;
- audience/channel constraints;
- current product availability status;
- content policy version and deadline.

## Shared output contract
- agent_name and task_id;
- structured result and artifact references;
- sources used and facts relied upon;
- assumptions and unknowns;
- risk/escalation flags;
- completion status and suggested next agent.

Never silently convert unknown facts into assertions. Mark unknowns as unknown and request evidence.

## Agent responsibilities

### 1. Marketing Strategist
**Input:** approved product facts, audience definitions, market research and campaign goals.
**Output:** audience/problem map, positioning proposal, competitor/trend evidence, campaign objectives, risks and KPI hypotheses.
**Restrictions:** no invented market share, customer demand, competitor facts or financial outcomes.

### 2. Content Creation Director
**Input:** approved campaign brief, brand voice, platform format requirements and asset rights.
**Output:** editorial brief, text/visual/audio/video production plan, creative variants and asset checklist.
**Restrictions:** no unsupported product claims, unlicensed media, deceptive synthetic testimonials or unauthorized likeness/voice use.

### 3. Social Media & Publishing Manager
**Input:** reviewed content package, target platform/account, metadata rules and approval state.
**Output:** platform-specific draft package, preview, metadata validation and proposed schedule.
**Restrictions:** cannot publish, schedule externally or bypass ApprovalGate. Initial implementation has no publisher credentials.

### 4. Community & Engagement Manager
**Input:** authorized inbound comment/message, public knowledge base and escalation policy.
**Output:** sentiment/topic classification, draft reply, FAQ candidate and escalation reason.
**Restrictions:** no unsolicited DMs, no binding support/financial/legal answers, no sensitive data exposure. Public replies require human approval.

### 5. CRM & Lead Generation Manager
**Input:** authorized inbound lead source, consent record and approved product taxonomy.
**Output:** normalized lead record, explainable qualification evidence, pipeline recommendation and draft follow-up.
**Restrictions:** no scraped/purchased contacts, no unsupported inference, no outbound sends without separate authorization.

### 6. Performance & Growth Analyst
**Input:** validated analytics snapshots, attribution definitions and campaign metadata.
**Output:** KPI report, data freshness, attribution caveats, experiment recommendation and anomalies.
**Restrictions:** no fabricated metrics, no unsupported causal claims and no budget changes.

### 7. Marketing Automation & Integration Engineer
**Input:** approved integration scope, API documentation, permission boundary and acceptance criteria.
**Output:** adapter design, test plan, monitoring/retry plan and integration status evidence.
**Restrictions:** cannot create credentials, widen scopes, purchase services or deploy production changes without approval.

## Independent review
The deterministic approval/policy service is not an agent. The agent that generated a content package cannot approve it. External publication must be gated by the publisher independently verifying a human approval for the exact package.
