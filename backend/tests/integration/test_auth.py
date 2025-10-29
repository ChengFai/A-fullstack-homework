import json
import os
import sys

import pytest
from fastapi import status
from httpx import AsyncClient

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.security.passwords import hash_password
from app.storage import db


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

    async def test_register_invalid_role(self, async_client: AsyncClient, clean_db):
        """测试无效角色注册"""
        invalid_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "invalid_role",
        }

        response = await async_client.post("/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid role"

    async def test_register_missing_fields(self, async_client: AsyncClient, clean_db):
        """测试缺少必填字段的注册"""
        incomplete_data = {
            "email": "test@example.com",
            "username": "testuser",
            # 缺少password和role
        }

        response = await async_client.post("/auth/register", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_invalid_email_format(
        self, async_client: AsyncClient, clean_db
    ):
        """测试无效邮箱格式注册"""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }

        response = await async_client.post("/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_success(self, async_client: AsyncClient, clean_db):
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
        assert "password" not in data["user"]

    async def test_login_wrong_password(self, async_client: AsyncClient, clean_db):
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

    async def test_login_user_not_found(self, async_client: AsyncClient, clean_db):
        """测试不存在的用户登录"""
        login_data = {"email": "nonexistent@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "User not found"

    async def test_login_suspended_user(self, async_client: AsyncClient, clean_db):
        """测试暂停用户登录"""
        # 先注册用户
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }
        register_response = await async_client.post(
            "/auth/register", json=register_data
        )
        user_id = register_response.json()["user"]["id"]

        # 暂停用户
        await db.set_user_suspended(user_id, True)

        # 尝试登录
        login_data = {"email": "test@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data["detail"] == "User suspended"

    async def test_login_missing_fields(self, async_client: AsyncClient, clean_db):
        """测试缺少必填字段的登录"""
        incomplete_data = {
            "email": "test@example.com"
            # 缺少password
        }

        response = await async_client.post("/auth/login", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_me_endpoint_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试获取当前用户信息成功"""
        response = await async_client.get("/auth/me", headers=auth_headers_employee)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "role" in data
        assert data["role"] == "employee"
        assert "password" not in data

    async def test_me_endpoint_unauthorized(self, async_client: AsyncClient, clean_db):
        """测试未授权访问me端点"""
        response = await async_client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_endpoint_invalid_token(
        self, async_client: AsyncClient, clean_db, invalid_auth_headers
    ):
        """测试无效令牌访问me端点"""
        response = await async_client.get("/auth/me", headers=invalid_auth_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_endpoint_employer_role(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试雇主角色访问me端点"""
        response = await async_client.get("/auth/me", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "employer"

    async def test_token_contains_correct_claims(
        self, async_client: AsyncClient, clean_db
    ):
        """测试令牌包含正确的声明"""
        # 注册用户
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }
        response = await async_client.post("/auth/register", json=register_data)

        token = response.json()["token"]

        # 解码令牌验证声明
        from app.security.jwt import decode_access_token

        decoded = decode_access_token(token)

        assert decoded["sub"] == response.json()["user"]["id"]
        assert decoded["role"] == "employee"
        assert "iat" in decoded
        assert "exp" in decoded

    async def test_login_token_different_from_register_token(
        self, async_client: AsyncClient, clean_db
    ):
        """测试登录和注册产生的令牌不同"""
        # 注册用户
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }
        register_response = await async_client.post(
            "/auth/register", json=register_data
        )
        register_token = register_response.json()["token"]

        # 登录用户
        login_data = {"email": "test@example.com", "password": "password123"}
        login_response = await async_client.post("/auth/login", json=login_data)
        login_token = login_response.json()["token"]

        # 令牌应该不同（因为签发时间不同）
        assert register_token != login_token

        # 但都应该有效
        from app.security.jwt import decode_access_token

        register_decoded = decode_access_token(register_token)
        login_decoded = decode_access_token(login_token)

        assert register_decoded["sub"] == login_decoded["sub"]
        assert register_decoded["role"] == login_decoded["role"]

    async def test_register_employee_and_employer_roles(
        self, async_client: AsyncClient, clean_db
    ):
        """测试注册员工和雇主角色"""
        # 注册员工
        employee_data = {
            "email": "employee@example.com",
            "username": "employee",
            "password": "password123",
            "role": "employee",
        }
        employee_response = await async_client.post(
            "/auth/register", json=employee_data
        )
        assert employee_response.status_code == status.HTTP_200_OK
        assert employee_response.json()["user"]["role"] == "employee"

        # 注册雇主
        employer_data = {
            "email": "employer@example.com",
            "username": "employer",
            "password": "password123",
            "role": "employer",
        }
        employer_response = await async_client.post(
            "/auth/register", json=employer_data
        )
        assert employer_response.status_code == status.HTTP_200_OK
        assert employer_response.json()["user"]["role"] == "employer"

    async def test_password_hashing_in_registration(
        self, async_client: AsyncClient, clean_db
    ):
        """测试注册时密码被正确哈希"""
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "role": "employee",
        }

        await async_client.post("/auth/register", json=register_data)

        # 直接从数据库获取用户验证密码哈希
        user = await db.get_user_by_email("test@example.com")
        assert user is not None
        assert user.password_hash != "password123"  # 密码应该被哈希
        assert len(user.password_hash) > 20  # 哈希后的密码应该很长

        # 验证密码哈希是否正确
        from app.security.passwords import verify_password

        assert verify_password("password123", user.password_hash) is True
        assert verify_password("wrongpassword", user.password_hash) is False
