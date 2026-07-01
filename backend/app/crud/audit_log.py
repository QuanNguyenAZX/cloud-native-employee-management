import uuid
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.models import AuditLog, User


def _actor_label(current_user: User | None) -> str:
    if not current_user:
        return "System"
    if current_user.is_superuser or current_user.role == "admin":
        return "Admin"
    if current_user.role == "manager":
        return "Manager"
    return "Employee"


def _actor_role(current_user: User | None) -> str | None:
    if not current_user:
        return None
    role = getattr(current_user.role, "value", current_user.role)
    return str(role)


def create_audit_log(
    *,
    session: Session,
    current_user: User | None,
    actor_id: uuid.UUID | None = None,
    actor_email: str | None = None,
    actor_role: str | None = None,
    actor_label: str | None = None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    detail: str | None = None,
    before_data: Any = None,
    after_data: Any = None,
) -> AuditLog:
    actor = current_user if current_user else None
    resolved_actor_id = (
        actor_id if actor_id is not None else (actor.id if actor else None)
    )
    resolved_actor_email = (
        actor_email if actor_email is not None else (actor.email if actor else None)
    )
    resolved_actor_role = (
        actor_role if actor_role is not None else _actor_role(actor)
    )
    resolved_actor_label = (
        actor_label if actor_label is not None else _actor_label(actor)
    )
    audit_log = AuditLog(
        actor_id=resolved_actor_id,
        actor_email=resolved_actor_email,
        actor_role=resolved_actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail or f"{resolved_actor_label} {action} {entity_type}",
        before_data=jsonable_encoder(before_data) if before_data is not None else None,
        after_data=jsonable_encoder(after_data) if after_data is not None else None,
    )
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    return audit_log
