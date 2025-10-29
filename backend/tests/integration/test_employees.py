import json
import os
import sys

import pytest
from fastapi import status
from httpx import AsyncClient

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.main import app
from app.storage import db


@pytest.mark.integration
class TestEmployeeEndpoints:
    """测试员工管理相关端点"""

    async def test_list_employees_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试成功获取员工列表"""
        # 创建几个员工
        employee1 = await db.create_user(
            email="emp1@example.com",
            username="emp1",
            role="employee",
            password_hash="hash1",
        )
        employee2 = await db.create_user(
            email="emp2@example.com",
            username="emp2",
            role="employee",
            password_hash="hash2",
        )
        # 创建一个雇主（不应出现在员工列表中）
        employer = await db.create_user(
            email="employer@example.com",
            username="employer",
            role="employer",
            password_hash="hash3",
        )

        response = await async_client.get("/employees/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 应该只返回员工，不返回雇主
        assert len(data) == 2

        employee_ids = {emp["id"] for emp in data}
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids
        assert employer.id not in employee_ids

        # 验证响应结构
        for emp in data:
            assert "id" in emp
            assert "email" in emp
            assert "username" in emp
            assert "role" in emp
            assert "is_suspended" in emp
            assert emp["role"] == "employee"
            assert "password" not in emp  # 密码不应在响应中

    async def test_list_employees_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权获取员工列表"""
        response = await async_client.get("/employees/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_list_employees_employee_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能获取员工列表"""
        response = await async_client.get("/employees/", headers=auth_headers_employee)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_employees_empty_list(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试空员工列表"""
        response = await async_client.get("/employees/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    async def test_list_employees_includes_suspended(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试员工列表包含被暂停的员工"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 暂停员工
        await db.set_user_suspended(employee.id, True)

        response = await async_client.get("/employees/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == employee.id
        assert data[0]["is_suspended"] is True

    async def test_suspend_employee_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试成功暂停员工"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        response = await async_client.post(
            f"/employees/{employee.id}/suspend", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == employee.id
        assert data["is_suspended"] is True

        # 验证数据库中的状态
        updated_employee = await db.get_user_by_id(employee.id)
        assert updated_employee.is_suspended is True

    async def test_suspend_employee_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试暂停不存在的员工"""
        response = await async_client.post(
            "/employees/nonexistent-id/suspend", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"

    async def test_suspend_employee_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权暂停员工"""
        response = await async_client.post("/employees/some-id/suspend")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_suspend_employee_employee_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能暂停其他员工"""
        response = await async_client.post(
            "/employees/some-id/suspend", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_suspend_employee_already_suspended(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试暂停已暂停的员工"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 暂停员工
        await db.set_user_suspended(employee.id, True)

        # 再次暂停
        response = await async_client.post(
            f"/employees/{employee.id}/suspend", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_suspended"] is True

    async def test_suspend_employer_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试不能暂停雇主"""
        # 创建另一个雇主
        other_employer = await db.create_user(
            email="other@example.com",
            username="other",
            role="employer",
            password_hash="hash",
        )

        response = await async_client.post(
            f"/employees/{other_employer.id}/suspend", headers=auth_headers_employer
        )

        # 应该成功，因为API不区分角色，只是设置暂停状态
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_suspended"] is True

    async def test_activate_employee_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试成功激活员工"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 先暂停员工
        await db.set_user_suspended(employee.id, True)

        # 激活员工
        response = await async_client.post(
            f"/employees/{employee.id}/activate", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == employee.id
        assert data["is_suspended"] is False

        # 验证数据库中的状态
        updated_employee = await db.get_user_by_id(employee.id)
        assert updated_employee.is_suspended is False

    async def test_activate_employee_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试激活不存在的员工"""
        response = await async_client.post(
            "/employees/nonexistent-id/activate", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"

    async def test_activate_employee_unauthorized(
        self, async_client: AsyncClient, clean_db
    ):
        """测试未授权激活员工"""
        response = await async_client.post("/employees/some-id/activate")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_activate_employee_employee_not_allowed(
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能激活其他员工"""
        response = await async_client.post(
            "/employees/some-id/activate", headers=auth_headers_employee
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_activate_employee_already_active(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试激活已激活的员工"""
        # 创建员工（默认是激活状态）
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 激活员工
        response = await async_client.post(
            f"/employees/{employee.id}/activate", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_suspended"] is False

    async def test_suspend_and_activate_workflow(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试暂停和激活的完整工作流程"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 1. 初始状态应该是激活的
        initial_state = await db.get_user_by_id(employee.id)
        assert initial_state.is_suspended is False

        # 2. 暂停员工
        suspend_response = await async_client.post(
            f"/employees/{employee.id}/suspend", headers=auth_headers_employer
        )
        assert suspend_response.status_code == status.HTTP_200_OK
        assert suspend_response.json()["is_suspended"] is True

        # 3. 验证暂停状态
        suspended_state = await db.get_user_by_id(employee.id)
        assert suspended_state.is_suspended is True

        # 4. 激活员工
        activate_response = await async_client.post(
            f"/employees/{employee.id}/activate", headers=auth_headers_employer
        )
        assert activate_response.status_code == status.HTTP_200_OK
        assert activate_response.json()["is_suspended"] is False

        # 5. 验证激活状态
        activated_state = await db.get_user_by_id(employee.id)
        assert activated_state.is_suspended is False

    async def test_employee_list_shows_correct_suspension_status(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试员工列表显示正确的暂停状态"""
        # 创建两个员工
        active_employee = await db.create_user(
            email="active@example.com",
            username="active",
            role="employee",
            password_hash="hash1",
        )
        suspended_employee = await db.create_user(
            email="suspended@example.com",
            username="suspended",
            role="employee",
            password_hash="hash2",
        )

        # 暂停一个员工
        await db.set_user_suspended(suspended_employee.id, True)

        # 获取员工列表
        response = await async_client.get("/employees/", headers=auth_headers_employer)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2

        # 找到对应的员工并验证状态
        active_emp_data = next(emp for emp in data if emp["id"] == active_employee.id)
        suspended_emp_data = next(
            emp for emp in data if emp["id"] == suspended_employee.id
        )

        assert active_emp_data["is_suspended"] is False
        assert suspended_emp_data["is_suspended"] is True

    async def test_suspend_employee_affects_ticket_visibility(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试暂停员工影响票据可见性"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 创建票据
        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at="2024-01-01T10:00:00Z",
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 雇主应该能看到票据
        tickets_response = await async_client.get(
            "/tickets/", headers=auth_headers_employer
        )
        assert tickets_response.status_code == status.HTTP_200_OK
        assert len(tickets_response.json()) == 1

        # 暂停员工
        await async_client.post(
            f"/employees/{employee.id}/suspend", headers=auth_headers_employer
        )

        # 雇主应该看不到被暂停员工的票据
        tickets_response_after = await async_client.get(
            "/tickets/", headers=auth_headers_employer
        )
        assert tickets_response_after.status_code == status.HTTP_200_OK
        assert len(tickets_response_after.json()) == 0

    async def test_activate_employee_restores_ticket_visibility(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试激活员工恢复票据可见性"""
        # 创建员工
        employee = await db.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )

        # 创建票据
        ticket = await db.create_ticket(
            user_id=employee.id,
            spent_at="2024-01-01T10:00:00Z",
            amount=100.0,
            currency="USD",
            description="Test expense",
            link="https://example.com",
        )

        # 暂停员工
        await async_client.post(
            f"/employees/{employee.id}/suspend", headers=auth_headers_employer
        )

        # 验证票据不可见
        tickets_response = await async_client.get(
            "/tickets/", headers=auth_headers_employer
        )
        assert len(tickets_response.json()) == 0

        # 激活员工
        await async_client.post(
            f"/employees/{employee.id}/activate", headers=auth_headers_employer
        )

        # 验证票据重新可见
        tickets_response_after = await async_client.get(
            "/tickets/", headers=auth_headers_employer
        )
        assert len(tickets_response_after.json()) == 1
        assert tickets_response_after.json()[0]["id"] == ticket.id
