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
class TestEmployeeEndpoints:
    """测试员工管理相关端点"""

    async def test_list_employees_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, db_session: AsyncSession
    ):
        """测试成功获取员工列表"""
        # 创建几个员工
        db_service = DatabaseService(db_session)
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
        # 创建一个雇主（不应出现在员工列表中）
        employer = await db_service.create_user(
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
        assert str(employee1.id) in employee_ids
        assert str(employee2.id) in employee_ids
        assert str(employer.id) not in employee_ids

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
        self, async_client: AsyncClient, clean_db, auth_headers_employee
    ):
        """测试员工不能访问员工列表"""
        response = await async_client.get("/employees/", headers=auth_headers_employee)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_suspend_employee_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, db_session: AsyncSession
    ):
        """测试成功暂停员工"""
        # 创建员工
        db_service = DatabaseService(db_session)
        employee = await db_service.create_user(
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

        # 验证员工被暂停
        assert data["is_suspended"] is True
        assert data["id"] == str(employee.id)

    async def test_activate_employee_success(
        self, async_client: AsyncClient, clean_db, auth_headers_employer, db_session: AsyncSession
    ):
        """测试成功激活员工"""
        # 创建并暂停员工
        db_service = DatabaseService(db_session)
        employee = await db_service.create_user(
            email="emp@example.com",
            username="emp",
            role="employee",
            password_hash="hash",
        )
        await db_service.set_user_suspended(employee.id, True)

        response = await async_client.post(
            f"/employees/{employee.id}/activate", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 验证员工被激活
        assert data["is_suspended"] is False
        assert data["id"] == str(employee.id)

    async def test_suspend_employee_not_found(
        self, async_client: AsyncClient, clean_db, auth_headers_employer
    ):
        """测试暂停不存在的员工"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.post(
            f"/employees/{fake_id}/suspend", headers=auth_headers_employer
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND