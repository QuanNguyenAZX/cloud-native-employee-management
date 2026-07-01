import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import RefreshToken


def create_refresh_token(
    *,
    session: Session,
    user_id: uuid.UUID,
    jti: str,
    expires_at: datetime,
) -> RefreshToken:
    db_obj = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_refresh_token_by_jti(*, session: Session, jti: str) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.jti == jti)
    return session.exec(statement).first()


def revoke_refresh_token(
    *, session: Session, db_refresh_token: RefreshToken
) -> RefreshToken:
    db_refresh_token.revoked_at = datetime.now(timezone.utc)
    session.add(db_refresh_token)
    session.commit()
    session.refresh(db_refresh_token)
    return db_refresh_token
