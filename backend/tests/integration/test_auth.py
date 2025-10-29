import json
import os
import sys

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.db_service import DatabaseService


@pytest.mark.integration
class TestAuthEndpoints:
    """测试认证相关端点"""

    async def test_register_success(
        self, async_client: AsyncClient, clean_db, sample_register_data
    ):
        """测试成功注册"""
        response = await async_client.post("/auth/register", json=sample_register_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_register_data["email"]
        assert data["user"]["username"] == sample_register_data["username"]
        assert data["user"]["role"] == sample_register_data["role"]
        assert "id" in data["user"]
        assert "password" not in data["user"]  # 密码不应在响应中

    async def test_register_duplicate_email(
        self, async_client: AsyncClient, clean_db, sample_register_data
    ):
        """测试重复邮箱注册"""
        # 第一次注册
        await async_client.post("/auth/register", json=sample_register_data)

        # 第二次注册相同邮箱
        response = await async_client.post("/auth/register", json=sample_register_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"] == "User already exists"

    async def test_login_success(self, async_client: AsyncClient, clean_db, db_session: AsyncSession):
        """测试成功登录"""
        # 先注册用户
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }
        await async_client.post("/auth/register", json=register_data)

        # 登录
        login_data = {"email": "test@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == login_data["email"]
        assert data["user"]["username"] == "testuser"
        assert data["user"]["role"] == "employee"
        assert "id" in data["user"]
        assert "password" not in data["user"]  # 密码不应在响应中

    async def test_login_wrong_password(self, async_client: AsyncClient, clean_db, db_session: AsyncSession):
        """测试错误密码登录"""
        # 先注册用户
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }
        await async_client.post("/auth/register", json=register_data)

        # 使用错误密码登录
        login_data = {"email": "test@example.com", "password": "wrongpassword"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Wrong password"

    async def test_login_user_not_found(self, async_client: AsyncClient, clean_db, db_session: AsyncSession):
        """测试不存在的用户登录"""
        login_data = {"email": "nonexistent@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "User not found"

    async def test_login_forbidden_when_user_suspended(self, async_client: AsyncClient, clean_db, db_session: AsyncSession):
        """测试被暂停用户禁止登录"""
        # 先注册用户
        register_data = {
            "email": "suspendme@example.com",
            "username": "suspendme",
            "password": "password123",
            "role": "employee",
        }
        await async_client.post("/auth/register", json=register_data)

        # 将用户设为暂停
        db_service = DatabaseService(db_session)
        existing = await db_service.get_user_by_email("suspendme@example.com")
        assert existing is not None
        await db_service.set_user_suspended(existing.id, True)

        # 尝试登录
        login_data = {"email": "suspendme@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data["detail"] == "您的账户已被停用，请联系管理员"

    async def test_me_endpoint_success(self, async_client: AsyncClient, clean_db, auth_headers_employee):
        """测试获取当前用户信息"""
        response = await async_client.get("/auth/me", headers=auth_headers_employee)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "role" in data
        assert "is_suspended" in data
        assert "password" not in data  # 密码不应在响应中
        assert data["role"] == "employee"

    async def test_me_endpoint_unauthorized(self, async_client: AsyncClient, clean_db, db_session: AsyncSession):
        """测试未授权访问me端点"""
        response = await async_client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED