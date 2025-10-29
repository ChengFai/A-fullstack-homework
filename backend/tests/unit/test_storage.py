import asyncio
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from unittest.mock import mock_open, patch

import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.storage import FileDB, Ticket, User, now_utc


class TestUserModel:
    """测试User模型"""

    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            id="user123",
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == "employee"
        assert user.password_hash == "hashed_password"
        assert user.is_suspended is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_to_dict(self):
        """测试用户转换为字典"""
        user = User(
            id="user123",
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        user_dict = user.to_dict()
        assert user_dict["id"] == "user123"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["username"] == "testuser"
        assert user_dict["role"] == "employee"
        assert user_dict["password_hash"] == "hashed_password"
        assert user_dict["is_suspended"] is False
        assert isinstance(user_dict["created_at"], str)
        assert isinstance(user_dict["updated_at"], str)

    def test_user_from_dict(self):
        """测试从字典创建用户"""
        user_dict = {
            "id": "user123",
            "email": "test@example.com",
            "username": "testuser",
            "role": "employee",
            "password_hash": "hashed_password",
            "is_suspended": False,
            "created_at": "2024-01-01T10:00:00+00:00",
            "updated_at": "2024-01-01T10:00:00+00:00",
        }

        user = User.from_dict(user_dict)
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == "employee"
        assert user.password_hash == "hashed_password"
        assert user.is_suspended is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_roundtrip_conversion(self):
        """测试用户字典转换的往返"""
        original_user = User(
            id="user123",
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        user_dict = original_user.to_dict()
        restored_user = User.from_dict(user_dict)

        assert restored_user.id == original_user.id
        assert restored_user.email == original_user.email
        assert restored_user.username == original_user.username
        assert restored_user.role == original_user.role
        assert restored_user.password_hash == original_user.password_hash
        assert restored_user.is_suspended == original_user.is_suspended


class TestTicketModel:
    """测试Ticket模型"""

    def test_ticket_creation(self):
        """测试票据创建"""
        spent_at = datetime.now(timezone.utc)
        ticket = Ticket(
            id="ticket123",
            user_id="user123",
            spent_at=spent_at,
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        assert ticket.id == "ticket123"
        assert ticket.user_id == "user123"
        assert ticket.spent_at == spent_at
        assert ticket.amount == 100.0
        assert ticket.currency == "USD"
        assert ticket.description == "Test expense"
        assert ticket.link == "https://example.com"
        assert ticket.status == "pending"
        assert ticket.is_soft_deleted is False
        assert isinstance(ticket.created_at, datetime)
        assert isinstance(ticket.updated_at, datetime)

    def test_ticket_to_dict(self):
        """测试票据转换为字典"""
        spent_at = datetime.now(timezone.utc)
        ticket = Ticket(
            id="ticket123",
            user_id="user123",
            spent_at=spent_at,
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        ticket_dict = ticket.to_dict()
        assert ticket_dict["id"] == "ticket123"
        assert ticket_dict["user_id"] == "user123"
        assert ticket_dict["amount"] == 100.0
        assert ticket_dict["currency"] == "USD"
        assert ticket_dict["description"] == "Test expense"
        assert ticket_dict["link"] == "https://example.com"
        assert ticket_dict["status"] == "pending"
        assert ticket_dict["is_soft_deleted"] is False
        assert isinstance(ticket_dict["spent_at"], str)
        assert isinstance(ticket_dict["created_at"], str)
        assert isinstance(ticket_dict["updated_at"], str)

    def test_ticket_from_dict(self):
        """测试从字典创建票据"""
        spent_at_str = "2024-01-01T10:00:00+00:00"
        ticket_dict = {
            "id": "ticket123",
            "user_id": "user123",
            "spent_at": spent_at_str,
            "amount": 100.0,
            "currency": "USD",
            "description": "Test expense",
            "link": "https://example.com",
            "status": "pending",
            "is_soft_deleted": False,
            "created_at": "2024-01-01T10:00:00+00:00",
            "updated_at": "2024-01-01T10:00:00+00:00",
        }

        ticket = Ticket.from_dict(ticket_dict)
        assert ticket.id == "ticket123"
        assert ticket.user_id == "user123"
        assert isinstance(ticket.spent_at, datetime)
        assert ticket.amount == 100.0
        assert ticket.currency == "USD"
        assert ticket.description == "Test expense"
        assert ticket.link == "https://example.com"
        assert ticket.status == "pending"
        assert ticket.is_soft_deleted is False
        assert isinstance(ticket.created_at, datetime)
        assert isinstance(ticket.updated_at, datetime)


class TestFileDB:
    """测试FileDB类"""

    @pytest.fixture
    async def temp_db(self):
        """创建临时数据库用于测试"""
        temp_dir = tempfile.mkdtemp()
        db = FileDB(temp_dir)
        yield db
        shutil.rmtree(temp_dir)

    async def test_create_user_success(self, temp_db):
        """测试成功创建用户"""
        user = await temp_db.create_user(
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
        assert len(user.id) > 0

    async def test_create_user_duplicate_email(self, temp_db):
        """测试创建重复邮箱用户"""
        await temp_db.create_user(
            email="test@example.com",
            username="testuser1",
            role="employee",
            password_hash="hashed_password1",
        )

        with pytest.raises(ValueError, match="email_exists"):
            await temp_db.create_user(
                email="test@example.com",
                username="testuser2",
                role="employee",
                password_hash="hashed_password2",
            )

    async def test_get_user_by_email(self, temp_db):
        """测试通过邮箱获取用户"""
        created_user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        found_user = await temp_db.get_user_by_email("test@example.com")
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    async def test_get_user_by_email_not_found(self, temp_db):
        """测试获取不存在的用户"""
        found_user = await temp_db.get_user_by_email("nonexistent@example.com")
        assert found_user is None

    async def test_get_user_by_id(self, temp_db):
        """测试通过ID获取用户"""
        created_user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        found_user = await temp_db.get_user_by_id(created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    async def test_get_user_by_id_not_found(self, temp_db):
        """测试获取不存在的用户ID"""
        found_user = await temp_db.get_user_by_id("nonexistent_id")
        assert found_user is None

    async def test_set_user_suspended(self, temp_db):
        """测试设置用户暂停状态"""
        created_user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        # 暂停用户
        suspended_user = await temp_db.set_user_suspended(created_user.id, True)
        assert suspended_user is not None
        assert suspended_user.is_suspended is True

        # 验证状态已保存
        found_user = await temp_db.get_user_by_id(created_user.id)
        assert found_user.is_suspended is True

    async def test_set_user_suspended_not_found(self, temp_db):
        """测试暂停不存在的用户"""
        result = await temp_db.set_user_suspended("nonexistent_id", True)
        assert result is None

    async def test_list_employees(self, temp_db):
        """测试列出员工"""
        # 创建员工和雇主
        employee1 = await temp_db.create_user(
            email="emp1@example.com",
            username="emp1",
            role="employee",
            password_hash="hash1",
        )
        employee2 = await temp_db.create_user(
            email="emp2@example.com",
            username="emp2",
            role="employee",
            password_hash="hash2",
        )
        employer = await temp_db.create_user(
            email="employer@example.com",
            username="employer",
            role="employer",
            password_hash="hash3",
        )

        employees = await temp_db.list_employees()
        assert len(employees) == 2
        employee_ids = {emp.id for emp in employees}
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids
        assert employer.id not in employee_ids

    async def test_list_employees_with_suspension_filter(self, temp_db):
        """测试按暂停状态过滤员工"""
        active_employee = await temp_db.create_user(
            email="active@example.com",
            username="active",
            role="employee",
            password_hash="hash1",
        )
        suspended_employee = await temp_db.create_user(
            email="suspended@example.com",
            username="suspended",
            role="employee",
            password_hash="hash2",
        )

        # 暂停一个员工
        await temp_db.set_user_suspended(suspended_employee.id, True)

        # 测试获取所有员工
        all_employees = await temp_db.list_employees()
        assert len(all_employees) == 2

        # 测试获取活跃员工
        active_employees = await temp_db.list_employees(include_suspended=False)
        assert len(active_employees) == 1
        assert active_employees[0].id == active_employee.id

        # 测试获取暂停员工
        suspended_employees = await temp_db.list_employees(include_suspended=True)
        assert len(suspended_employees) == 1
        assert suspended_employees[0].id == suspended_employee.id

    async def test_create_ticket(self, temp_db):
        """测试创建票据"""
        user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        spent_at = datetime.now(timezone.utc)
        ticket = await temp_db.create_ticket(
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
        assert len(ticket.id) > 0

    async def test_get_ticket(self, temp_db):
        """测试获取票据"""
        user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        created_ticket = await temp_db.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        found_ticket = await temp_db.get_ticket(created_ticket.id)
        assert found_ticket is not None
        assert found_ticket.id == created_ticket.id
        assert found_ticket.user_id == created_ticket.user_id

    async def test_get_ticket_not_found(self, temp_db):
        """测试获取不存在的票据"""
        found_ticket = await temp_db.get_ticket("nonexistent_id")
        assert found_ticket is None

    async def test_list_tickets(self, temp_db):
        """测试列出票据"""
        user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        ticket1 = await temp_db.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense 1",
            link="https://example1.com",
        )

        ticket2 = await temp_db.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=200.0,
            currency="USD",
            description="Test expense 2",
            link="https://example2.com",
        )

        tickets = await temp_db.list_tickets()
        assert len(tickets) == 2
        ticket_ids = {t.id for t in tickets}
        assert ticket1.id in ticket_ids
        assert ticket2.id in ticket_ids

    async def test_update_ticket(self, temp_db):
        """测试更新票据"""
        user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        ticket = await temp_db.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Original description",
            link="https://original.com",
        )

        # 更新票据
        updated_ticket = await temp_db.update_ticket(
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

    async def test_update_ticket_not_found(self, temp_db):
        """测试更新不存在的票据"""
        result = await temp_db.update_ticket("nonexistent_id", amount=100.0)
        assert result is None

    async def test_soft_delete_ticket(self, temp_db):
        """测试软删除票据"""
        user = await temp_db.create_user(
            email="test@example.com",
            username="testuser",
            role="employee",
            password_hash="hashed_password",
        )

        ticket = await temp_db.create_ticket(
            user_id=user.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        deleted_ticket = await temp_db.soft_delete_ticket(ticket.id)
        assert deleted_ticket is not None
        assert deleted_ticket.is_soft_deleted is True

        # 验证票据仍然存在但被标记为删除
        found_ticket = await temp_db.get_ticket(ticket.id)
        assert found_ticket.is_soft_deleted is True

    async def test_soft_delete_ticket_not_found(self, temp_db):
        """测试软删除不存在的票据"""
        result = await temp_db.soft_delete_ticket("nonexistent_id")
        assert result is None


class TestNowUTC:
    """测试now_utc函数"""

    def test_now_utc_returns_datetime(self):
        """测试now_utc返回datetime对象"""
        now = now_utc()
        assert isinstance(now, datetime)
        assert now.tzinfo is not None
        assert now.tzinfo.utcoffset(None).total_seconds() == 0  # UTC时区

    def test_now_utc_is_recent(self):
        """测试now_utc返回最近的时间"""
        now = now_utc()
        current_time = datetime.now(timezone.utc)
        time_diff = abs((current_time - now).total_seconds())
        assert time_diff < 1  # 应该在1秒内
