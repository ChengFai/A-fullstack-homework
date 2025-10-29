import json
import os
import sys
from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.db_service import DatabaseService


@pytest.mark.integration
class TestTicketEndpoints:
    """测试票据相关端点"""

    async def test_create_ticket_success(
        self,
        async_client: AsyncClient,
        clean_db,
        auth_headers_employee,
        sample_ticket_data,
    ):
        """测试成功创建票据"""
        response = await async_client.post(
            "/tickets/", json=sample_ticket_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert "id" in data
        assert data["user_id"] is not None
        assert data["spent_at"] == sample_ticket_data["spent_at"]
        assert data["amount"] == sample_ticket_data["amount"]
        assert data["currency"] == sample_ticket_data["currency"]
        assert data["description"] == sample_ticket_data["description"]
        assert data["link"] == sample_ticket_data["link"]
        assert data["status"] == "pending"
        assert data["is_soft_deleted"] is False
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_ticket_unauthorized(
        self, async_client: AsyncClient, clean_db, sample_ticket_data
    ):
        """测试未授权创建票据"""
        response = await async_client.post("/tickets/", json=sample_ticket_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_ticket_employer_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, sample_ticket_data
    ):
        """测试雇主不能创建票据"""
        response = await async_client.post(
            "/tickets/", json=sample_ticket_data, headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_tickets_employee_view_own_only(
        self, async_client: AsyncClient, clean_db, auth_headers_employee, db_session: AsyncSession
    ):
        """测试员工只能看到自己的票据"""
        # 创建两个用户
        db_service = DatabaseService(db_session)
        user1 = await db_service.create_user(
            email="user1@example.com",
            username="user1",
            role="employee",
            password_hash="hash1",
        )
        user2 = await db_service.create_user(
            email="user2@example.com",
            username="user2",
            role="employee",
            password_hash="hash2",
        )

        # 为两个用户创建票据
        ticket1 = await db_service.create_ticket(
            user_id=user1.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="User1 expense",
            link="https://example1.com",
        )
        ticket2 = await db_service.create_ticket(
            user_id=user2.id,
            spent_at=datetime.now(timezone.utc),
            amount=200.0,
            currency="USD",
            description="User2 expense",
            link="https://example2.com",
        )

        # 使用user1的认证头获取票据列表
        from app.security.jwt import create_access_token
        token = create_access_token(str(user1.id), {"role": "employee"})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/tickets/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 应该只看到user1的票据
        assert len(data) == 1
        assert data[0]["id"] == str(ticket1.id)
        assert data[0]["user_id"] == str(user1.id)

    async def test_list_tickets_employer_view_all(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, db_session: AsyncSession
    ):
        """测试雇主可以看到所有票据"""
        # 创建员工和票据
        db_service = DatabaseService(db_session)
        employee = await db_service.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        ticket = await db_service.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Employee expense",
            link="https://example.com",
        )

        response = await async_client.get("/tickets/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 应该看到员工的票据
        assert len(data) == 1
        assert data[0]["id"] == str(ticket.id)
        assert data[0]["user_id"] == str(employee.id)

    async def test_get_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee, test_ticket
    ):
        """测试成功获取票据"""
        response = await async_client.get(
            f"/tickets/{test_ticket.id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证响应结构
        assert data["id"] == str(test_ticket.id)
        assert data["user_id"] == str(test_ticket.user_id)
        assert data["amount"] == test_ticket.amount
        assert data["currency"] == test_ticket.currency
        assert data["description"] == test_ticket.description
        assert data["link"] == test_ticket.link
        assert data["status"] == test_ticket.status

    async def test_get_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试获取不存在的票据"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(
            f"/tickets/{fake_id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee, test_ticket
    ):
        """测试成功更新票据"""
        update_data = {
            "spent_at": "2024-01-02T10:00:00Z",
            "amount": 150.0,
            "currency": "EUR",
            "description": "Updated expense",
            "link": "https://updated.com",
        }

        response = await async_client.put(
            f"/tickets/{test_ticket.id}", json=update_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证更新后的数据
        assert data["amount"] == update_data["amount"]
        assert data["currency"] == update_data["currency"]
        assert data["description"] == update_data["description"]
        assert data["link"] == update_data["link"]

    async def test_delete_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee, test_ticket
    ):
        """测试成功删除票据"""
        response = await async_client.delete(
            f"/tickets/{test_ticket.id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证票据被软删除
        assert data["is_soft_deleted"] is True

    async def test_approve_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, test_ticket
    ):
        """测试成功批准票据"""
        response = await async_client.post(
            f"/tickets/{test_ticket.id}/approve", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证票据状态
        assert data["status"] == "approved"

    async def test_deny_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, test_ticket
    ):
        """测试成功拒绝票据"""
        response = await async_client.post(
            f"/tickets/{test_ticket.id}/deny", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证票据状态
        assert data["status"] == "denied"