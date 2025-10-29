from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import User as UserModel, Ticket as TicketModel


class DatabaseService:
    """数据库服务层，提供与SQLAlchemy模型交互的方法"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # User 相关方法
    async def create_user(
        self, email: str, username: str, role: str, password_hash: str
    ) -> UserModel:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("email_exists")

        user = UserModel(
            email=email,
            username=username,
            role=role,
            password_hash=password_hash,
            is_suspended=False,  # 明确设置为False，确保新用户默认是正常状态
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """根据邮箱获取用户"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserModel]:
        """根据ID获取用户"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def set_user_suspended(self, user_id: UUID, suspended: bool) -> Optional[UserModel]:
        """设置用户暂停状态"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_suspended=suspended, updated_at=datetime.utcnow())
            .returning(UserModel)
        )
        user = result.scalar_one_or_none()
        if user:
            await self.session.commit()
        return user

    async def list_employees(
        self, include_suspended: Optional[bool] = None
    ) -> List[UserModel]:
        """获取员工列表"""
        query = select(UserModel).where(UserModel.role == "employee")
        
        if include_suspended is not None:
            query = query.where(UserModel.is_suspended == include_suspended)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    # Ticket 相关方法
    async def create_ticket(
        self,
        user_id: UUID,
        spent_at: datetime,
        amount: float,
        currency: str,
        description: Optional[str],
        link: Optional[str],
    ) -> TicketModel:
        """创建新票据"""
        ticket = TicketModel(
            user_id=user_id,
            spent_at=spent_at,
            amount=amount,
            currency=currency,
            description=description,
            link=link,
        )
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def get_ticket(self, ticket_id: UUID) -> Optional[TicketModel]:
        """根据ID获取票据"""
        result = await self.session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def list_tickets(self) -> List[TicketModel]:
        """获取所有票据"""
        result = await self.session.execute(select(TicketModel))
        return result.scalars().all()

    async def list_tickets_by_user(self, user_id: UUID) -> List[TicketModel]:
        """获取指定用户的票据"""
        result = await self.session.execute(
            select(TicketModel).where(TicketModel.user_id == user_id)
        )
        return result.scalars().all()

    async def update_ticket(self, ticket_id: UUID, **fields) -> Optional[TicketModel]:
        """更新票据"""
        # 过滤掉None值
        update_fields = {k: v for k, v in fields.items() if v is not None}
        if not update_fields:
            return await self.get_ticket(ticket_id)
        
        update_fields["updated_at"] = datetime.utcnow()
        
        result = await self.session.execute(
            update(TicketModel)
            .where(TicketModel.id == ticket_id)
            .values(**update_fields)
            .returning(TicketModel)
        )
        ticket = result.scalar_one_or_none()
        if ticket:
            await self.session.commit()
        return ticket

    async def soft_delete_ticket(self, ticket_id: UUID) -> Optional[TicketModel]:
        """软删除票据"""
        return await self.update_ticket(ticket_id, is_soft_deleted=True)

    async def approve_ticket(self, ticket_id: UUID) -> Optional[TicketModel]:
        """批准票据"""
        return await self.update_ticket(ticket_id, status="approved")

    async def deny_ticket(self, ticket_id: UUID) -> Optional[TicketModel]:
        """拒绝票据"""
        return await self.update_ticket(ticket_id, status="denied")

    async def get_tickets_for_suspended_users(self) -> List[TicketModel]:
        """获取被暂停用户的票据（用于软删除）"""
        # 这里需要JOIN查询，获取被暂停用户的票据
        result = await self.session.execute(
            select(TicketModel)
            .join(UserModel, TicketModel.user_id == UserModel.id)
            .where(UserModel.is_suspended == True)
        )
        return result.scalars().all()
