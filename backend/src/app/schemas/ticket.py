from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    spent_at: datetime
    amount: float = Field(gt=0)
    currency: str = Field(min_length=1)
    description: Optional[str] = None
    link: Optional[str] = None


class TicketUpdate(BaseModel):
    spent_at: Optional[datetime] = None
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None


class TicketPublic(BaseModel):
    id: str
    user_id: str
    spent_at: datetime
    amount: float
    currency: str
    description: Optional[str]
    link: Optional[str]
    status: str
    is_soft_deleted: bool
    created_at: datetime
    updated_at: datetime
