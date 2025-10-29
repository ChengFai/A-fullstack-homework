from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(description="employee|employer")
    username: str = Field(min_length=1)


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
    is_suspended: bool


class AuthResponse(BaseModel):
    token: str
    user: UserPublic
