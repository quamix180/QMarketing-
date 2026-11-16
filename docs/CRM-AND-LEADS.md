# CRM and Lead Management Specification

## Scope
The initial CRM workflow is inbound-first. It may capture and classify leads only from authorized forms, approved integrations, events, newsletters and inbound inquiries. Outbound communication remains draft-only until separately approved.

## Lead categories
- Institutional investors.
- Asset owners and issuers.
- Startups seeking financing.
- RWA technology partners.
- Financial institutions.
- Family offices and funds.
- Retail users and community members.

These are segmentation labels, not proof of investment suitability, qualification or intent.

## Pipeline
New Lead -> Qualified -> Contacted -> Engaged -> Meeting Scheduled -> Proposal -> Negotiation -> Won / Lost / Nurture.

## Minimum record
- Lead/organization ID.
- Contact details only where necessary.
- Source and capture timestamp.
- Market/geography and sector.
- Stated interest and requested service.
- Qualification evidence and score explanation.
- Interaction history and responsible owner.
- Consent/legal basis, channel preferences and opt-out state.
- Next action and due date.
- Retention/deletion status.

## Qualification model
Use an explainable 0-100 score with documented evidence, not inferred sensitive traits:
- Fit to QUAMIX's currently available products/services: 0-30.
- Explicitly stated use case: 0-25.
- Decision-maker/role evidence: 0-15.
- Timing stated by the prospect: 0-15.
- Completeness and consent/source quality: 0-15.

Unknown information receives zero points; do not hallucinate or infer it. Score is a triage aid, not an investment or credit assessment. Human review is required before commercial commitments.

## Restrictions
- No purchased/scraped contact lists without legal review.
- No unsolicited bulk messaging.
- No fabricated meetings, relationships, interest or commitments.
- Do not store sensitive personal data unless a reviewed, necessary lawful basis exists.
- Honor opt-outs, deletion requests and retention limits.
- Investor inquiries, financial proposals, pricing and regulated-service questions must be escalated.
