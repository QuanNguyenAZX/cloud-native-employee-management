import math
from typing import Any, Literal, cast

from fastapi import APIRouter, Depends
from sqlalchemy import asc, desc, or_
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import AuditLog
from app.schemas import AuditLogPublic, AuditLogsPublic

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/", response_model=AuditLogsPublic)
def read_audit_logs(
    session: SessionDep,
    page: int = 1,
    size: int = 20,
    search: str | None = None,
    entity_type: str | None = None,
    action: Literal["created", "updated", "deleted"] | None = None,
    sort_order: Literal["asc", "desc"] = "desc",
) -> Any:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    sort_fn = asc if sort_order == "asc" else desc
    detail = cast(Any, AuditLog.detail)
    actor_email = cast(Any, AuditLog.actor_email)
    actor_role = cast(Any, AuditLog.actor_role)
    entity_type_col = cast(Any, AuditLog.entity_type)
    entity_id = cast(Any, AuditLog.entity_id)
    action_col = cast(Any, AuditLog.action)
    created_at = cast(Any, AuditLog.created_at)

    statement = select(AuditLog)
    count_statement = select(func.count()).select_from(AuditLog)

    if search:
        pattern = f"%{search.strip()}%"
        search_filter = or_(
            detail.ilike(pattern),
            actor_email.ilike(pattern),
            actor_role.ilike(pattern),
            entity_type_col.ilike(pattern),
            entity_id.ilike(pattern),
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    if entity_type:
        entity_type_pattern = f"%{entity_type.strip()}%"
        statement = statement.where(entity_type_col.ilike(entity_type_pattern))
        count_statement = count_statement.where(entity_type_col.ilike(entity_type_pattern))

    if action:
        statement = statement.where(action_col == action)
        count_statement = count_statement.where(action_col == action)

    count = session.exec(count_statement).one()
    logs = session.exec(
        statement.order_by(sort_fn(created_at))
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    data = [AuditLogPublic.model_validate(item) for item in logs]
    pages = math.ceil(count / size) if count else 1
    return AuditLogsPublic(data=data, count=count, page=page, size=size, pages=pages)
