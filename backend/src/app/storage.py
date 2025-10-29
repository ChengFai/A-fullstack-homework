import asyncio
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    id: str
    email: str
    username: str
    role: str  # 'employee' | 'employer'
    password_hash: str
    is_suspended: bool = False
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def to_dict(self) -> dict:
        """转换为字典，处理 datetime 序列化"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """从字典创建 User 对象，处理 datetime 反序列化"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class Ticket:
    id: str
    user_id: str
    spent_at: datetime
    amount: float
    currency: str
    description: Optional[str] = None
    link: Optional[str] = None
    status: str = "pending"  # 'pending' | 'approved' | 'denied'
    is_soft_deleted: bool = False
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def to_dict(self) -> dict:
        """转换为字典，处理 datetime 序列化"""
        data = asdict(self)
        data["spent_at"] = self.spent_at.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """从字典创建 Ticket 对象，处理 datetime 反序列化"""
        data["spent_at"] = datetime.fromisoformat(data["spent_at"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class FileDB:
    def __init__(self, data_dir: str = "data") -> None:
        self._lock = asyncio.Lock()
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.tickets_file = os.path.join(data_dir, "tickets.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 初始化内存缓存
        self.users_by_email: Dict[str, User] = {}
        self.users_by_id: Dict[str, User] = {}
        self.tickets_by_id: Dict[str, Ticket] = {}

        # 从文件加载数据
        self._load_data()

    def _load_data(self) -> None:
        """从文件加载数据到内存"""
        # 加载用户数据
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User.from_dict(user_data)
                        self.users_by_email[user.email] = user
                        self.users_by_id[user.id] = user
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"警告：加载用户数据失败，将使用空数据: {e}")

        # 加载票据数据
        if os.path.exists(self.tickets_file):
            try:
                with open(self.tickets_file, "r", encoding="utf-8") as f:
                    tickets_data = json.load(f)
                    for ticket_data in tickets_data:
                        ticket = Ticket.from_dict(ticket_data)
                        self.tickets_by_id[ticket.id] = ticket
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"警告：加载票据数据失败，将使用空数据: {e}")

    async def _save_users(self) -> None:
        """保存用户数据到文件"""
        users_data = [user.to_dict() for user in self.users_by_id.values()]
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)

    async def _save_tickets(self) -> None:
        """保存票据数据到文件"""
        tickets_data = [ticket.to_dict() for ticket in self.tickets_by_id.values()]
        with open(self.tickets_file, "w", encoding="utf-8") as f:
            json.dump(tickets_data, f, ensure_ascii=False, indent=2)

    async def create_user(
        self, email: str, username: str, role: str, password_hash: str
    ) -> User:
        async with self._lock:
            if email in self.users_by_email:
                raise ValueError("email_exists")
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                role=role,
                password_hash=password_hash,
            )
            self.users_by_email[email] = user
            self.users_by_id[user.id] = user
            await self._save_users()
            return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self._lock:
            return self.users_by_email.get(email)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        async with self._lock:
            return self.users_by_id.get(user_id)

    async def set_user_suspended(self, user_id: str, suspended: bool) -> Optional[User]:
        async with self._lock:
            user = self.users_by_id.get(user_id)
            if not user:
                return None
            user.is_suspended = suspended
            user.updated_at = now_utc()
            await self._save_users()
            return user

    async def list_employees(
        self, include_suspended: Optional[bool] = None
    ) -> List[User]:
        async with self._lock:
            users = [u for u in self.users_by_id.values() if u.role == "employee"]
            if include_suspended is None:
                return users
            return [u for u in users if u.is_suspended == include_suspended]

    async def create_ticket(
        self,
        user_id: str,
        spent_at: datetime,
        amount: float,
        currency: str,
        description: Optional[str],
        link: Optional[str],
    ) -> Ticket:
        async with self._lock:
            ticket = Ticket(
                id=str(uuid.uuid4()),
                user_id=user_id,
                spent_at=spent_at,
                amount=amount,
                currency=currency,
                description=description,
                link=link,
            )
            self.tickets_by_id[ticket.id] = ticket
            await self._save_tickets()
            return ticket

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        async with self._lock:
            return self.tickets_by_id.get(ticket_id)

    async def list_tickets(self) -> List[Ticket]:
        async with self._lock:
            return list(self.tickets_by_id.values())

    async def update_ticket(self, ticket_id: str, **fields) -> Optional[Ticket]:
        async with self._lock:
            t = self.tickets_by_id.get(ticket_id)
            if not t:
                return None
            for k, v in fields.items():
                if hasattr(t, k) and v is not None:
                    setattr(t, k, v)
            t.updated_at = now_utc()
            await self._save_tickets()
            return t

    async def soft_delete_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return await self.update_ticket(ticket_id, is_soft_deleted=True)


# 使用文件存储作为临时方案，未来可无缝切换到真实数据库
db = FileDB()
