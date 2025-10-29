from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserPublic
from ..security.dependencies import get_current_user
from ..security.jwt import create_access_token
from ..security.passwords import hash_password, verify_password
from ..storage import db

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    existing = await db.get_user_by_email(payload.email)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if existing.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User suspended"
        )

    if not verify_password(payload.password, existing.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password"
        )

    token = create_access_token(existing.id, {"role": existing.role})
    return AuthResponse(
        token=token,
        user=UserPublic(
            id=existing.id,
            email=existing.email,
            username=existing.username,
            role=existing.role,
        ),
    )


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest):
    # 检查用户是否已存在
    existing = await db.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    # 验证角色
    if payload.role not in ("employee", "employer"):
        raise HTTPException(status_code=400, detail="Invalid role")

    # 创建新用户
    user = await db.create_user(
        email=payload.email,
        username=payload.username,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )

    token = create_access_token(user.id, {"role": user.role})
    return AuthResponse(
        token=token,
        user=UserPublic(
            id=user.id, email=user.email, username=user.username, role=user.role
        ),
    )


@router.get("/me", response_model=UserPublic)
async def me(user=Depends(get_current_user)):
    return UserPublic(
        id=user.id, email=user.email, username=user.username, role=user.role
    )
