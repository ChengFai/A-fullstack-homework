from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.user import UserPublic
from ..security.dependencies import require_role
from ..storage import User, db

router = APIRouter()


def to_public(u: User) -> UserPublic:
    return UserPublic(
        id=u.id,
        email=u.email,
        username=u.username,
        role=u.role,
        is_suspended=u.is_suspended,
    )


@router.get("/", response_model=List[UserPublic])
async def list_employees(_: User = Depends(require_role("employer"))):
    users = await db.list_employees()
    return [to_public(u) for u in users]


@router.post("/{user_id}/suspend", response_model=UserPublic)
async def suspend_employee(user_id: str, _: User = Depends(require_role("employer"))):
    user = await db.set_user_suspended(user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_public(user)


@router.post("/{user_id}/activate", response_model=UserPublic)
async def activate_employee(user_id: str, _: User = Depends(require_role("employer"))):
    user = await db.set_user_suspended(user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_public(user)
