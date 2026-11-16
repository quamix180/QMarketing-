"""In-memory content lifecycle state machine; deliberately no external side effects."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .approval import Approval, ApprovalGate, PublicationPackage


class WorkflowError(ValueError):
    """Raised when a content lifecycle transition is invalid."""


@dataclass(frozen=True)
class ContentWorkflow:
    package: PublicationPackage
    status: str = "IDEA"
    approval: Optional[Approval] = None
    history: tuple[str, ...] = ("IDEA",)


_TRANSITIONS = {
    "IDEA": {"RESEARCHED"},
    "RESEARCHED": {"PLANNED"},
    "PLANNED": {"DRAFTED"},
    "DRAFTED": {"ASSETS_GENERATED", "QUALITY_CHECKED"},
    "ASSETS_GENERATED": {"QUALITY_CHECKED"},
    "QUALITY_CHECKED": {"AWAITING_APPROVAL"},
    "AWAITING_APPROVAL": {"APPROVED", "REJECTED", "REVISION_REQUIRED"},
    "REVISION_REQUIRED": {"DRAFTED"},
    "APPROVED": {"SCHEDULED"},
    "SCHEDULED": {"READY_TO_PUBLISH"},
    "REJECTED": set(),
    # READY_TO_PUBLISH is the terminal state of this offline core. No publisher exists here.
    "READY_TO_PUBLISH": set(),
}


def transition(
    workflow: ContentWorkflow,
    target: str,
    *,
    gate: Optional[ApprovalGate] = None,
    approval: Optional[Approval] = None,
) -> ContentWorkflow:
    """Advance one allowed step. Approval is revalidated at approval and handoff."""
    if target not in _TRANSITIONS.get(workflow.status, set()):
        raise WorkflowError(f"invalid transition: {workflow.status} -> {target}")

    selected_approval = workflow.approval
    if target == "APPROVED":
        if gate is None or approval is None:
            raise WorkflowError("human approval and approval gate are required")
        try:
            gate.validate(workflow.package, approval)
        except ValueError as exc:
            raise WorkflowError(f"approval validation failed: {exc}") from exc
        selected_approval = approval

    if target in {"SCHEDULED", "READY_TO_PUBLISH"}:
        if gate is None or selected_approval is None:
            raise WorkflowError("valid approval is required before publication handoff")
        try:
            gate.validate(workflow.package, selected_approval)
        except ValueError as exc:
            raise WorkflowError(f"approval revalidation failed: {exc}") from exc

    return ContentWorkflow(
        package=workflow.package,
        status=target,
        approval=selected_approval,
        history=workflow.history + (target,),
    )
