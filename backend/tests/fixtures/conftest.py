import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.storage import Ticket, User, db


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建一个事件循环用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def clean_db() -> AsyncGenerator[None, None]:
    """清理数据库，确保每个测试都有干净的环境"""
    # 清理所有数据
    db.users.clear()
    db.tickets.clear()
    db.next_user_id = 1
    db.next_ticket_id = 1
    yield
    # 测试后再次清理
    db.users.clear()
    db.tickets.clear()
    db.next_user_id = 1
    db.next_ticket_id = 1


@pytest.fixture
def test_client() -> TestClient:
    """创建同步测试客户端"""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user_employee(clean_db) -> User:
    """创建一个测试员工用户"""
    user = await db.create_user(
        email="employee@test.com",
        username="test_employee",
        role="employee",
        password_hash="$pbkdf2-sha256$29000$test_hash$test_salt",
    )
    return user


@pytest.fixture
async def test_user_employer(clean_db) -> User:
    """创建一个测试雇主用户"""
    user = await db.create_user(
        email="employer@test.com",
        username="test_employer",
        role="employer",
        password_hash="$pbkdf2-sha256$29000$test_hash$test_salt",
    )
    return user


@pytest.fixture
async def test_ticket(test_user_employee) -> Ticket:
    """创建一个测试票据"""
    ticket = await db.create_ticket(
        user_id=test_user_employee.id,
        spent_at="2024-01-01T10:00:00Z",
        amount=100.0,
        currency="USD",
        description="Test expense",
        link="https://example.com",
    )
    return ticket


@pytest.fixture
def auth_headers_employee(test_user_employee) -> dict:
    """员工用户的认证头"""
    from app.security.jwt import create_access_token

    token = create_access_token(test_user_employee.id, {"role": "employee"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_employer(test_user_employer) -> dict:
    """雇主用户的认证头"""
    from app.security.jwt import create_access_token

    token = create_access_token(test_user_employer.id, {"role": "employer"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def invalid_auth_headers() -> dict:
    """无效的认证头"""
    return {"Authorization": "Bearer invalid_token"}


@pytest.fixture
def sample_login_data() -> dict:
    """示例登录数据"""
    return {"email": "test@example.com", "password": "testpassword123"}


@pytest.fixture
def sample_register_data() -> dict:
    """示例注册数据"""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
        "role": "employee",
    }


@pytest.fixture
def sample_ticket_data() -> dict:
    """示例票据数据"""
    return {
        "spent_at": "2024-01-01T10:00:00Z",
        "amount": 150.0,
        "currency": "USD",
        "description": "Business lunch",
        "link": "https://restaurant.com/receipt",
    }
