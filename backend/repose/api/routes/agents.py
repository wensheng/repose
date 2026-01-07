from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from repose.api import deps
from repose.models.agent_event import AgentEvent
from repose.models.repository import Repository

router = APIRouter()

class AgentEventSchema(BaseModel):
    id: UUID
    repo_id: UUID
    event_type: str
    agent_name: str | None
    confidence: float
    description: str | None
    is_reviewed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/events", response_model=List[AgentEventSchema])
async def list_agent_events(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List detected agent events.
    """
    stmt = select(AgentEvent).order_by(AgentEvent.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

class AgentAction(BaseModel):
    action: str  # "approve", "revert", "fix"

@router.post("/events/{event_id}/action")
async def take_agent_action(
    event_id: UUID,
    action: AgentAction,
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = select(AgentEvent).filter(AgentEvent.id == event_id)
    result = await db.execute(stmt)
    event = result.scalars().first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Logic for actions
    if action.action == "approve":
        event.is_reviewed = True
        event.review_status = "approved"
    elif action.action == "revert":
        event.is_reviewed = True
        event.review_status = "reverted"
        # TODO: Trigger GitHub Revert API
        print(f"Triggering REVERT for {event.source_ref}")
    elif action.action == "fix":
        event.is_reviewed = True
        event.review_status = "fix_requested"
        # TODO: Trigger LLM Fix Agent
        print(f"Triggering FIX Agent for {event.source_ref}")
        
    await db.commit()
    return {"status": "success", "action": action.action}
