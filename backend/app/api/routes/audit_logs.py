import math
from typing import Any, Literal

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

    statement = select(AuditLog)
    count_statement = select(func.count()).select_from(AuditLog)

    if search:
        pattern = f"%{search.strip()}%"
        search_filter = or_(
            AuditLog.detail.ilike(pattern),
            AuditLog.actor_email.ilike(pattern),
            AuditLog.actor_role.ilike(pattern),
            AuditLog.entity_type.ilike(pattern),
            AuditLog.entity_id.ilike(pattern),
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    if entity_type:
        statement = statement.where(
            AuditLog.entity_type.ilike(f"%{entity_type.strip()}%")
        )
        count_statement = count_statement.where(
            AuditLog.entity_type.ilike(f"%{entity_type.strip()}%")
        )

    if action:
        statement = statement.where(AuditLog.action == action)
        count_statement = count_statement.where(AuditLog.action == action)

    count = session.exec(count_statement).one()
    logs = session.exec(
        statement.order_by(sort_fn(AuditLog.created_at))
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    data = [AuditLogPublic.model_validate(item) for item in logs]
    pages = math.ceil(count / size) if count else 1
    return AuditLogsPublic(data=data, count=count, page=page, size=size, pages=pages)
