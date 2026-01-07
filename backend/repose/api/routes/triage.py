from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from uuid import UUID

from repose.api import deps
from repose.core.config import settings
from repose.core.llm import create_llm_client, LLMConfig
from repose.core.triage.service import TriageService
from repose.models.issue import Issue

router = APIRouter()

class IssueSchema(BaseModel):
    id: UUID
    number: int
    title: str
    triage_status: str
    priority: str | None
    tags: List[str] | None
    summary: str | None
    
    class Config:
        from_attributes = True

@router.get("/issues", response_model=List[IssueSchema])
async def list_issues(
    db: AsyncSession = Depends(deps.get_db),
    status: str = None
):
    stmt = select(Issue)
    if status:
        stmt = stmt.filter(Issue.triage_status == status)
    stmt = stmt.order_by(Issue.priority.desc(), Issue.created_at.desc()) # Simple sorting
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/issues/{issue_id}/analyze")
async def analyze_issue_endpoint(
    issue_id: UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    stmt = select(Issue).filter(Issue.id == issue_id)
    result = await db.execute(stmt)
    issue = result.scalars().first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    # Init LLM
    llm_config = LLMConfig(
        provider="gemini",
        model="gemini-2.0-flash",
        api_key=settings.GEMINI_API_KEY
    )
    llm_client = create_llm_client(llm_config)
    
    service = TriageService(db, llm_client)
    analyzed_issue = await service.analyze_issue(issue)
    
    return analyzed_issue
