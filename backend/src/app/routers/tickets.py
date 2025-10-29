from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.ticket import TicketCreate, TicketPublic, TicketUpdate
from ..security.dependencies import get_current_user, require_role
from ..storage import Ticket, User, db

router = APIRouter()


def ticket_to_public(t: Ticket) -> TicketPublic:
    return TicketPublic(
        id=t.id,
        user_id=t.user_id,
        spent_at=t.spent_at,
        amount=t.amount,
        currency=t.currency,
        description=t.description,
        link=t.link,
        status=t.status,
        is_soft_deleted=t.is_soft_deleted,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("/", response_model=List[TicketPublic])
async def list_tickets(current_user: User = Depends(get_current_user)):
    tickets = await db.list_tickets()
    if current_user.role == "employee":
        visible = [
            t for t in tickets if t.user_id == current_user.id and not t.is_soft_deleted
        ]
    else:  # employer
        # 过滤：不显示已软删或所属用户被停用的票据
        # 为避免并发深拷贝，这里逐条检查
        visible = []
        for t in tickets:
            if t.is_soft_deleted:
                continue
            owner = await db.get_user_by_id(t.user_id)
            if owner and not owner.is_suspended:
                visible.append(t)
    return [ticket_to_public(t) for t in visible]


@router.post("/", response_model=TicketPublic)
async def create_ticket(
    payload: TicketCreate, user: User = Depends(require_role("employee"))
):
    t = await db.create_ticket(
        user_id=user.id,
        spent_at=payload.spent_at,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        link=payload.link,
    )
    return ticket_to_public(t)


@router.get("/{ticket_id}", response_model=TicketPublic)
async def get_ticket(ticket_id: str, current_user: User = Depends(get_current_user)):
    t = await db.get_ticket(ticket_id)
    if not t or t.is_soft_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.role == "employee" and t.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    owner = await db.get_user_by_id(t.user_id)
    if current_user.role == "employer" and owner and owner.is_suspended:
        raise HTTPException(status_code=404, detail="Not found")
    return ticket_to_public(t)


@router.put("/{ticket_id}", response_model=TicketPublic)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    user: User = Depends(require_role("employee")),
):
    t = await db.get_ticket(ticket_id)
    if not t or t.is_soft_deleted or t.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    if t.status != "pending":
        raise HTTPException(
            status_code=409, detail="Only pending ticket can be updated"
        )
    updated = await db.update_ticket(
        ticket_id,
        spent_at=payload.spent_at,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        link=payload.link,
    )
    assert updated
    return ticket_to_public(updated)


@router.delete("/{ticket_id}", response_model=TicketPublic)
async def delete_ticket(ticket_id: str, user: User = Depends(require_role("employee"))):
    t = await db.get_ticket(ticket_id)
    if not t or t.is_soft_deleted or t.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    if t.status != "pending":
        raise HTTPException(
            status_code=409, detail="Only pending ticket can be deleted"
        )
    deleted = await db.soft_delete_ticket(ticket_id)
    assert deleted
    return ticket_to_public(deleted)


@router.post("/{ticket_id}/approve", response_model=TicketPublic)
async def approve_ticket(ticket_id: str, _: User = Depends(require_role("employer"))):
    t = await db.get_ticket(ticket_id)
    if not t or t.is_soft_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if t.status == "approved":
        return ticket_to_public(t)
    if t.status == "denied":
        raise HTTPException(status_code=409, detail="Already denied")
    updated = await db.update_ticket(ticket_id, status="approved")
    assert updated
    return ticket_to_public(updated)


@router.post("/{ticket_id}/deny", response_model=TicketPublic)
async def deny_ticket(ticket_id: str, _: User = Depends(require_role("employer"))):
    t = await db.get_ticket(ticket_id)
    if not t or t.is_soft_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if t.status == "denied":
        return ticket_to_public(t)
    if t.status == "approved":
        raise HTTPException(status_code=409, detail="Already approved")
    updated = await db.update_ticket(ticket_id, status="denied")
    assert updated
    return ticket_to_public(updated)
