import json
import os
import sys
from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import AsyncClient

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.storage import db


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
        self,
        async_client: AsyncClient,
        clean_db,
        auth_headers_employer,
        sample_ticket_data,
    ):
        """测试雇主不能创建票据"""
        response = await async_client.post(
            "/tickets/", json=sample_ticket_data, headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_ticket_missing_fields(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试缺少必填字段创建票据"""
        incomplete_data = {
            "spent_at": "2024-01-01T10:00:00Z",
            "amount": 100.0,
            # 缺少currency, description等
        }

        response = await async_client.post(
            "/tickets/", json=incomplete_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_ticket_invalid_amount(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试无效金额创建票据"""
        invalid_data = {
            "spent_at": "2024-01-01T10:00:00Z",
            "amount": -100.0,  # 负数金额
            "currency": "USD",
            "description": "Test expense",
            "link": "https://example.com",
        }

        response = await async_client.post(
            "/tickets/", json=invalid_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_ticket_invalid_date_format(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试无效日期格式创建票据"""
        invalid_data = {
            "spent_at": "invalid-date",
            "amount": 100.0,
            "currency": "USD",
            "description": "Test expense",
            "link": "https://example.com",
        }

        response = await async_client.post(
            "/tickets/", json=invalid_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_list_tickets_employee_view_own_only(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工只能看到自己的票据"""
        # 创建两个用户
        user1 = await db.create_user(
            email="user1@example.com",
            username="user1",
            role="employee",
            password_hash="hash1",
        )
        user2 = await db.create_user(
            email="user2@example.com",
            username="user2",
            role="employee",
            password_hash="hash2",
        )

        # 为两个用户创建票据
        ticket1 = await db.create_ticket(
            user_id=user1.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="User1 expense",
            link="https://example1.com",
        )
        ticket2 = await db.create_ticket(
            user_id=user2.id,
            spent_at=datetime.now(timezone.utc),
            amount=200.0,
            currency="USD",
            description="User2 expense",
            link="https://example2.com",
        )

        # 使用user1的认证头获取票据列表
        from app.security.jwt import create_access_token

        token = create_access_token(user1.id, {"role": "employee"})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/tickets/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 应该只看到user1的票据
        assert len(data) == 1
        assert data[0]["id"] == ticket1.id
        assert data[0]["user_id"] == user1.id

    async def test_list_tickets_employer_view_all(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试雇主可以看到所有票据"""
        # 创建员工用户
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        # 创建票据
        ticket = await db.create_ticket(
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

        # 应该看到所有票据
        assert len(data) == 1
        assert data[0]["id"] == ticket.id
        assert data[0]["user_id"] == employee.id

    async def test_list_tickets_employer_hides_suspended_user_tickets(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试雇主看不到被暂停用户的票据"""
        # 创建员工用户
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        # 创建票据
        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Employee expense",
            link="https://example.com",
        )

        # 暂停用户
        await db.set_user_suspended(employee.id, True)

        response = await async_client.get("/tickets/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 应该看不到被暂停用户的票据
        assert len(data) == 0

    async def test_list_tickets_hides_soft_deleted(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试不显示软删除的票据"""
        # 创建票据
        response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Test expense",
                "link": "https://example.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = response.json()["id"]

        # 软删除票据
        await db.soft_delete_ticket(ticket_id)

        # 获取票据列表
        list_response = await async_client.get(
            "/tickets/", headers=auth_headers_employee
        )

        assert list_response.status_code == status.HTTP_200_OK
        data = list_response.json()

        # 应该看不到软删除的票据
        assert len(data) == 0

    async def test_get_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试成功获取单个票据"""
        # 创建票据
        create_response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Test expense",
                "link": "https://example.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = create_response.json()["id"]

        # 获取票据
        response = await async_client.get(
            f"/tickets/{ticket_id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == ticket_id
        assert data["amount"] == 100.0
        assert data["description"] == "Test expense"

    async def test_get_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试获取不存在的票据"""
        response = await async_client.get(
            "/tickets/nonexistent-id", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_get_ticket_unauthorized(self, async_client: AsyncClient, clean_db):
        """测试未授权获取票据"""
        response = await async_client.get("/tickets/some-id")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_ticket_employee_cannot_access_others(
        self, async_client: AsyncClient, clean_db
    ):
        """测试员工不能访问其他人的票据"""
        # 创建两个员工用户
        user1 = await db.create_user(
            email="user1@example.com",
            username="user1",
            role="employee",
            password_hash="hash1",
        )
        user2 = await db.create_user(
            email="user2@example.com",
            username="user2",
            role="employee",
            password_hash="hash2",
        )

        # user2创建票据
        ticket = await db.create_ticket(
            user_id=user2.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="User2 expense",
            link="https://example.com",
        )

        # user1尝试访问user2的票据
        from app.security.jwt import create_access_token

        token = create_access_token(user1.id, {"role": "employee"})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/tickets/{ticket.id}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_update_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试成功更新票据"""
        # 创建票据
        create_response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Original description",
                "link": "https://original.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = create_response.json()["id"]

        # 更新票据
        update_data = {
            "spent_at": "2024-01-02T10:00:00Z",
            "amount": 150.0,
            "currency": "EUR",
            "description": "Updated description",
            "link": "https://updated.com",
        }

        response = await async_client.put(
            f"/tickets/{ticket_id}", json=update_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["amount"] == 150.0
        assert data["currency"] == "EUR"
        assert data["description"] == "Updated description"
        assert data["link"] == "https://updated.com"
        assert data["status"] == "pending"  # 状态不应改变

    async def test_update_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试更新不存在的票据"""
        update_data = {"amount": 150.0, "description": "Updated description"}

        response = await async_client.put(
            "/tickets/nonexistent-id", json=update_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_update_ticket_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权更新票据"""
        update_data = {"amount": 150.0, "description": "Updated description"}

        response = await async_client.put("/tickets/some-id", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_ticket_employer_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试雇主不能更新票据"""
        update_data = {"amount": 150.0, "description": "Updated description"}

        response = await async_client.put(
            "/tickets/some-id", json=update_data, headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_ticket_wrong_owner(self, async_client: AsyncClient, clean_db):
        """测试不能更新其他人的票据"""
        # 创建两个员工用户
        user1 = await db.create_user(
            email="user1@example.com",
            username="user1",
            role="employee",
            password_hash="hash1",
        )
        user2 = await db.create_user(
            email="user2@example.com",
            username="user2",
            role="employee",
            password_hash="hash2",
        )

        # user2创建票据
        ticket = await db.create_ticket(
            user_id=user2.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="User2 expense",
            link="https://example.com",
        )

        # user1尝试更新user2的票据
        from app.security.jwt import create_access_token

        token = create_access_token(user1.id, {"role": "employee"})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"amount": 150.0, "description": "Updated by user1"}

        response = await async_client.put(
            f"/tickets/{ticket.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_update_ticket_not_pending(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试不能更新非pending状态的票据"""
        # 创建票据
        create_response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Test expense",
                "link": "https://example.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = create_response.json()["id"]

        # 批准票据
        await db.update_ticket(ticket_id, status="approved")

        # 尝试更新已批准的票据
        update_data = {"amount": 150.0, "description": "Updated description"}

        response = await async_client.put(
            f"/tickets/{ticket_id}", json=update_data, headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"] == "Only pending ticket can be updated"

    async def test_delete_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试成功删除票据"""
        # 创建票据
        create_response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Test expense",
                "link": "https://example.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = create_response.json()["id"]

        # 删除票据
        response = await async_client.delete(
            f"/tickets/{ticket_id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["is_soft_deleted"] is True

        # 验证票据已被软删除
        ticket = await db.get_ticket(ticket_id)
        assert ticket.is_soft_deleted is True

    async def test_delete_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试删除不存在的票据"""
        response = await async_client.delete(
            "/tickets/nonexistent-id", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_delete_ticket_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权删除票据"""
        response = await async_client.delete("/tickets/some-id")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_ticket_employer_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试雇主不能删除票据"""
        response = await async_client.delete(
            "/tickets/some-id", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_ticket_not_pending(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试不能删除非pending状态的票据"""
        # 创建票据
        create_response = await async_client.post(
            "/tickets/",
            json={
                "spent_at": "2024-01-01T10:00:00Z",
                "amount": 100.0,
                "currency": "USD",
                "description": "Test expense",
                "link": "https://example.com",
            },
            headers=auth_headers_employee,
        )

        ticket_id = create_response.json()["id"]

        # 批准票据
        await db.update_ticket(ticket_id, status="approved")

        # 尝试删除已批准的票据
        response = await async_client.delete(
            f"/tickets/{ticket_id}", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"] == "Only pending ticket can be deleted"

    async def test_approve_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试成功批准票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 批准票据
        response = await async_client.post(
            f"/tickets/{ticket.id}/approve", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "approved"

        # 验证数据库中的状态
        updated_ticket = await db.get_ticket(ticket.id)
        assert updated_ticket.status == "approved"

    async def test_approve_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试批准不存在的票据"""
        response = await async_client.post(
            "/tickets/nonexistent-id/approve", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_approve_ticket_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权批准票据"""
        response = await async_client.post("/tickets/some-id/approve")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_approve_ticket_employee_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能批准票据"""
        response = await async_client.post(
            "/tickets/some-id/approve", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_approve_ticket_already_approved(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试批准已批准的票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 批准票据
        await db.update_ticket(ticket.id, status="approved")

        # 再次批准
        response = await async_client.post(
            f"/tickets/{ticket.id}/approve", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "approved"

    async def test_approve_ticket_already_denied(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试批准已拒绝的票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 拒绝票据
        await db.update_ticket(ticket.id, status="denied")

        # 尝试批准已拒绝的票据
        response = await async_client.post(
            f"/tickets/{ticket.id}/approve", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"] == "Already denied"

    async def test_deny_ticket_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试成功拒绝票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 拒绝票据
        response = await async_client.post(
            f"/tickets/{ticket.id}/deny", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "denied"

        # 验证数据库中的状态
        updated_ticket = await db.get_ticket(ticket.id)
        assert updated_ticket.status == "denied"

    async def test_deny_ticket_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试拒绝不存在的票据"""
        response = await async_client.post(
            "/tickets/nonexistent-id/deny", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

    async def test_deny_ticket_unauthorized(self, async_client: AsyncClient, clean_db):
        """测试未授权拒绝票据"""
        response = await async_client.post("/tickets/some-id/deny")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_deny_ticket_employee_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能拒绝票据"""
        response = await async_client.post(
            "/tickets/some-id/deny", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_deny_ticket_already_denied(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试拒绝已拒绝的票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 拒绝票据
        await db.update_ticket(ticket.id, status="denied")

        # 再次拒绝
        response = await async_client.post(
            f"/tickets/{ticket.id}/deny", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "denied"

    async def test_deny_ticket_already_approved(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试拒绝已批准的票据"""
        # 创建员工用户和票据
        employee = await db.create_user(
            email="employee@example.com",
            username="employee",
            role="employee",
            password_hash="hash",
        )

        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 批准票据
        await db.update_ticket(ticket.id, status="approved")

        # 尝试拒绝已批准的票据
        response = await async_client.post(
            f"/tickets/{ticket.id}/deny", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"] == "Already approved"
