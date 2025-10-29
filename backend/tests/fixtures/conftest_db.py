import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.models import Base, User as UserModel, Ticket as TicketModel
from app.db_service import DatabaseService
from app.security.passwords import hash_password
from app.security.jwt import create_access_token


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # 测试时不显示SQL
    future=True,
)

# 创建测试会话工厂
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建一个事件循环用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话"""
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async with TestSessionLocal() as session:
        yield session
    
    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def clean_db(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """清理数据库，确保每个测试都有干净的环境"""
    # 删除所有数据
    await db_session.execute("DELETE FROM tickets")
    await db_session.execute("DELETE FROM users")
    await db_session.commit()
    yield
    # 测试后再次清理
    await db_session.execute("DELETE FROM tickets")
    await db_session.execute("DELETE FROM users")
    await db_session.commit()


@pytest.fixture
def test_client() -> TestClient:
    """创建同步测试客户端"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user_employee(db_session: AsyncSession) -> UserModel:
    """创建一个测试员工用户"""
    db_service = DatabaseService(db_session)
    user = await db_service.create_user(
        email="employee@test.com",
        username="test_employee",
        role="employee",
        password_hash=hash_password("testpassword123"),
    )
    return user


@pytest_asyncio.fixture
async def test_user_employer(db_session: AsyncSession) -> UserModel:
    """创建一个测试雇主用户"""
    db_service = DatabaseService(db_session)
    user = await db_service.create_user(
        email="employer@test.com",
        username="test_employer",
        role="employer",
        password_hash=hash_password("testpassword123"),
    )
    return user


@pytest_asyncio.fixture
async def test_ticket(db_session: AsyncSession, test_user_employee: UserModel) -> TicketModel:
    """创建一个测试票据"""
    from datetime import datetime, timezone
    
    db_service = DatabaseService(db_session)
    ticket = await db_service.create_ticket(
        user_id=test_user_employee.id,
        spent_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        amount=100.0,
        currency="USD",
        description="Test expense",
        link="https://example.com",
    )
    return ticket


@pytest.fixture
def auth_headers_employee(test_user_employee: UserModel) -> dict:
    """员工用户的认证头"""
    token = create_access_token(str(test_user_employee.id), {"role": "employee"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_employer(test_user_employer: UserModel) -> dict:
    """雇主用户的认证头"""
    token = create_access_token(str(test_user_employer.id), {"role": "employer"})
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
