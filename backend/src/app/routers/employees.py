from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user import UserPublic
from ..security.dependencies import require_role
from ..models import User as UserModel
from ..database import get_db
from ..db_service import DatabaseService

router = APIRouter()


def to_public(u: UserModel) -> UserPublic:
    return UserPublic(
        id=str(u.id),
        email=u.email,
        username=u.username,
        role=u.role,
        is_suspended=u.is_suspended,
    )


@router.get("/", response_model=List[UserPublic])
async def list_employees(
    _: UserModel = Depends(require_role("employer")),
    db_session: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db_session)
    users = await db_service.list_employees()
    return [to_public(u) for u in users]


@router.post("/{user_id}/suspend", response_model=UserPublic)
async def suspend_employee(
    user_id: str, 
    _: UserModel = Depends(require_role("employer")),
    db_session: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db_session)
    user = await db_service.set_user_suspended(UUID(user_id), True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_public(user)


@router.post("/{user_id}/activate", response_model=UserPublic)
async def activate_employee(
    user_id: str, 
    _: UserModel = Depends(require_role("employer")),
    db_session: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db_session)
    user = await db_service.set_user_suspended(UUID(user_id), False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_public(user)
