#!/usr/bin/env python3
"""
数据库集成测试脚本
在安装Docker并启动PostgreSQL后运行此脚本测试数据库连接
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend" / "src"))

from app.database import engine, init_db
from app.db_service import DatabaseService
from app.models import User, Ticket
from app.security.passwords import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


async def test_database_integration():
    """测试数据库集成"""
    print("🚀 开始测试数据库集成...")
    
    try:
        # 初始化数据库
        print("📊 初始化数据库表...")
        await init_db()
        print("✅ 数据库表创建成功")
        
        # 创建会话
        AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with AsyncSessionLocal() as session:
            db_service = DatabaseService(session)
            
            # 测试用户创建
            print("👤 测试用户创建...")
            user = await db_service.create_user(
                email="test@example.com",
                username="testuser",
                role="employee",
                password_hash=hash_password("password123")
            )
            print(f"✅ 用户创建成功: {user.email}")
            
            # 测试票据创建
            print("🎫 测试票据创建...")
            from datetime import datetime
            ticket = await db_service.create_ticket(
                user_id=user.id,
                spent_at=datetime.now(),
                amount=100.50,
                currency="USD",
                description="测试票据",
                link="https://example.com"
            )
            print(f"✅ 票据创建成功: {ticket.id}")
            
            # 测试查询
            print("🔍 测试数据查询...")
            users = await db_service.list_employees()
            tickets = await db_service.list_tickets()
            print(f"✅ 查询成功: {len(users)} 个用户, {len(tickets)} 个票据")
            
            # 测试更新
            print("✏️ 测试数据更新...")
            updated_ticket = await db_service.approve_ticket(ticket.id)
            print(f"✅ 票据状态更新成功: {updated_ticket.status}")
            
            print("🎉 所有测试通过！数据库集成成功！")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """主函数"""
    print("=" * 50)
    print("PostgreSQL 数据库集成测试")
    print("=" * 50)
    
    # 检查环境变量
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password123@localhost:5432/expense_tracker")
    print(f"数据库连接字符串: {database_url}")
    
    success = await test_database_integration()
    
    if success:
        print("\n🎊 恭喜！数据库集成配置完成！")
        print("\n下一步:")
        print("1. 启动FastAPI服务器: cd backend && uv run uvicorn src.app.main:app --reload")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 测试API端点")
    else:
        print("\n💥 数据库集成测试失败，请检查:")
        print("1. PostgreSQL容器是否正在运行")
        print("2. 数据库连接配置是否正确")
        print("3. 网络连接是否正常")


if __name__ == "__main__":
    asyncio.run(main())
