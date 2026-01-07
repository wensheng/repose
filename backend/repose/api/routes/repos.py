from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from repose.api import deps
from repose.models.repository import Repository as RepoModel
from repose.schemas.repository import Repository, RepositoryCreate
from repose.core.config import settings
from repose.integrations.github import GitHubClient
from repose.workers.tasks import sync_repository

router = APIRouter()

@router.get("/available")
async def get_available_repos():
    """
    Fetch all personal repos owned by the configured GITHUB_USERNAME.
    """
    if not settings.GITHUB_USERNAME:
        raise HTTPException(status_code=400, detail="GITHUB_USERNAME not configured")
    
    client = GitHubClient(token=settings.GITHUB_PAT)
    try:
        repos = await client.get_user_repos(settings.GITHUB_USERNAME)
        # Filter/Map to a simpler schema if needed, strictly passing through for now 
        # but logically we might want to return just what the frontend needs.
        # Front end generic generic list.
        return repos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Repository])
async def read_repositories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
):
    result = await db.execute(select(RepoModel).offset(skip).limit(limit))
    repos = result.scalars().all()
    return repos

@router.post("/", response_model=Repository)
async def create_repository(
    repo_in: RepositoryCreate,
    db: AsyncSession = Depends(deps.get_db),
):
    # Check if repo exists
    result = await db.execute(select(RepoModel).filter(RepoModel.full_name == repo_in.full_name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Repository already registered")

    db_repo = RepoModel(**repo_in.model_dump())
    db.add(db_repo)
    await db.commit()
    await db.refresh(db_repo)
    
    # Trigger sync automatically
    sync_repository.delay(str(db_repo.id))
    
    return db_repo

@router.get("/{repo_id}", response_model=Repository)
async def read_repository(
    repo_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    result = await db.execute(select(RepoModel).filter(RepoModel.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.post("/{repo_id}/sync")
async def sync_repository_endpoint(
    repo_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    repo_result = await db.execute(select(RepoModel).filter(RepoModel.id == repo_id))
    repo = repo_result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    from app.workers.tasks import sync_repository
    task = sync_repository.delay(str(repo_id))
    
    return {"message": "Sync started", "task_id": task.id}

@router.post("/{repo_id}/sync-issues")
async def sync_repo_issues_endpoint(
    repo_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    repo_result = await db.execute(select(RepoModel).filter(RepoModel.id == repo_id))
    repo = repo_result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    from app.workers.tasks import sync_repo_issues
    task = sync_repo_issues.delay(str(repo_id))
    
    return {"message": "Issue Sync started", "task_id": task.id}
