import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.db_service import DatabaseService
from app.models import User, Ticket


@pytest.mark.unit
class TestDatabaseService:
    """测试数据库服务"""

    @pytest_asyncio.fixture
    async def db_service(self, db_session: AsyncSession) -> DatabaseService:
        """创建数据库服务实例"""
        return DatabaseService(db_session)

    async def test_create_user_success(self, db_service: DatabaseService):
        """测试成功创建用户"""
        user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == "employee"
        assert user.password_hash == "hashed_password"
        assert user.is_suspended is False
        assert user.id is not None
        assert isinstance(user.id, UUID)

    async def test_create_user_duplicate_email(self, db_service: DatabaseService):
        """测试创建重复邮箱用户"""
        await db_service.create_user(
            email="test@example.com",
            username="testuser1",
            role="employee",
            password_hash="hashed_password1",
        )

        with pytest.raises(ValueError, match="email_exists"):
            await db_service.create_user(
                email="test@example.com",
                username="testuser2",
                role="employee",
                password_hash="hashed_password2",
            )

    async def test_get_user_by_email(self, db_service: DatabaseService):
        """测试通过邮箱获取用户"""
        created_user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        found_user = await db_service.get_user_by_email("test@example.com")
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    async def test_get_user_by_email_not_found(self, db_service: DatabaseService):
        """测试获取不存在的用户"""
        found_user = await db_service.get_user_by_email("nonexistent@example.com")
        assert found_user is None

    async def test_set_user_suspended(self, db_service: DatabaseService):
        """测试设置用户暂停状态"""
        created_user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        # 暂停用户
        suspended_user = await db_service.set_user_suspended(created_user.id, True)
        assert suspended_user is not None
        assert suspended_user.is_suspended is True

        # 验证状态已保存
        found_user = await db_service.get_user_by_id(created_user.id)
        assert found_user.is_suspended is True

    async def test_list_employees(self, db_service: DatabaseService):
        """测试列出员工"""
        # 创建员工和雇主
        employee1 = await db_service.create_user(
            email="emp1@example.com",
            username="emp1",
            role="employee",
            password_hash="hash1",
        )
        employee2 = await db_service.create_user(
            email="emp2@example.com",
            username="emp2",
            role="employee",
            password_hash="hash2",
        )
        employer = await db_service.create_user(
            email="employer@example.com",
            username="employer",
            role="employer",
            password_hash="hash3",
        )

        employees = await db_service.list_employees()
        assert len(employees) == 2
        employee_ids = {emp.id for emp in employees}
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids
        assert employer.id not in employee_ids

    async def test_create_ticket(self, db_service: DatabaseService):
        """测试创建票据"""
        user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        spent_at = datetime.now(timezone.utc)
        ticket = await db_service.create_ticket(
            user_id=user.id,
            spent_at=spent_at,
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        assert ticket.user_id == user.id
        assert ticket.spent_at == spent_at
        assert ticket.amount == 100.0
        assert ticket.currency == "USD"
        assert ticket.description == "Test expense"
        assert ticket.link == "https://example.com"
        assert ticket.status == "pending"
        assert ticket.is_soft_deleted is False
        assert ticket.id is not None
        assert isinstance(ticket.id, UUID)

    async def test_get_ticket(self, db_service: DatabaseService):
        """测试获取票据"""
        user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        created_ticket = await db_service.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        found_ticket = await db_service.get_ticket(created_ticket.id)
        assert found_ticket is not None
        assert found_ticket.id == created_ticket.id
        assert found_ticket.user_id == created_ticket.user_id

    async def test_update_ticket(self, db_service: DatabaseService):
        """测试更新票据"""
        user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        ticket = await db_service.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Original description",
            link="https://original.com",
        )

        # 更新票据
        updated_ticket = await db_service.update_ticket(
            ticket.id,
            amount=150.0,
            description="Updated description",
            status="approved",
        )

        assert updated_ticket is not None
        assert updated_ticket.amount == 150.0
        assert updated_ticket.description == "Updated description"
        assert updated_ticket.status == "approved"
        assert updated_ticket.link == "https://original.com"  # 未更新的字段保持不变

    async def test_soft_delete_ticket(self, db_service: DatabaseService):
        """测试软删除票据"""
        user = await db_service.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        ticket = await db_service.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        deleted_ticket = await db_service.soft_delete_ticket(ticket.id)
        assert deleted_ticket is not None
        assert deleted_ticket.is_soft_deleted is True

        # 验证票据仍然存在但被标记为删除
        found_ticket = await db_service.get_ticket(ticket.id)
        assert found_ticket.is_soft_deleted is True
