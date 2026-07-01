import uuid
from os.path import splitext
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.storage import (
    StorageError,
    create_avatar_key,
    delete_object,
    upload_object,
)
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = session.exec(statement).all()

    users_public = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(
    *, session: SessionDep, user_in: UserCreate, current_user: CurrentUser
) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="created",
        entity_type="User",
        entity_id=str(user.id),
    )
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    before_data = current_user.model_dump()
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="User",
        entity_id=str(current_user.id),
        before_data=before_data,
        after_data=current_user.model_dump(),
    )
    return current_user


@router.post("/me/avatar", response_model=UserPublic)
async def update_user_avatar_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> Any:
    """
    Upload or replace the current user's avatar.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Avatar must be an image file")

    content = await file.read()
    if len(content) > settings.AVATAR_UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Avatar file is too large")

    suffix = splitext(file.filename or "")[1] or ".jpg"
    avatar_key = create_avatar_key(user_id=str(current_user.id), suffix=suffix)

    try:
        upload_object(
            key=avatar_key,
            content=content,
            content_type=file.content_type or "application/octet-stream",
        )
    except StorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    previous_key = current_user.avatar_key
    current_user.avatar_key = avatar_key
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="User",
        entity_id=str(current_user.id),
        before_data={"avatar_key": previous_key},
        after_data={"avatar_key": avatar_key},
    )

    if previous_key and previous_key != avatar_key:
        try:
            delete_object(key=previous_key)
        except StorageError:
            pass

    return current_user


@router.delete("/me/avatar", response_model=Message)
def delete_user_avatar_me(
    *, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Remove the current user's avatar.
    """
    previous_key = current_user.avatar_key
    current_user.avatar_key = None
    session.add(current_user)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="User",
        entity_id=str(current_user.id),
        before_data={"avatar_key": previous_key},
        after_data={"avatar_key": None},
    )

    if previous_key:
        try:
            delete_object(key=previous_key)
        except StorageError:
            pass

    return Message(message="Avatar removed successfully")


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="User",
        entity_id=str(current_user.id),
        before_data={"password_changed": True},
        after_data={"password_changed": True},
    )
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    actor_id = current_user.id
    actor_email = current_user.email
    actor_role = getattr(current_user.role, "value", current_user.role)
    actor_label = (
        "Admin"
        if str(actor_role) == "admin"
        else "Manager"
        if str(actor_role) == "manager"
        else "Employee"
    )
    before_data = current_user.model_dump()
    session.delete(current_user)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=None,
        actor_id=actor_id,
        actor_email=actor_email,
        actor_role=str(actor_role),
        actor_label=actor_label,
        action="deleted",
        entity_type="User",
        entity_id=str(actor_id),
        before_data=before_data,
    )
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    crud.create_audit_log(
        session=session,
        current_user=None,
        action="created",
        entity_type="User",
        entity_id=str(user.id),
        detail="System created User",
    )
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    before_data = db_user.model_dump()
    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="User",
        entity_id=str(db_user.id),
        before_data=before_data,
        after_data=db_user.model_dump(),
    )
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    actor_id = current_user.id
    actor_email = current_user.email
    actor_role = getattr(current_user.role, "value", current_user.role)
    actor_label = (
        "Admin"
        if str(actor_role) == "admin"
        else "Manager"
        if str(actor_role) == "manager"
        else "Employee"
    )
    before_data = user.model_dump()
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=None,
        actor_id=actor_id,
        actor_email=actor_email,
        actor_role=str(actor_role),
        actor_label=actor_label,
        action="deleted",
        entity_type="User",
        entity_id=str(user_id),
        before_data=before_data,
    )
    return Message(message="User deleted successfully")
