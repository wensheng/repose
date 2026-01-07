from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class RepositoryBase(BaseModel):
    provider: str
    org_name: str
    repo_name: str
    full_name: str
    default_branch: str = "main"
    is_active: bool = True

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(RepositoryBase):
    pass

class RepositoryInDBBase(RepositoryBase):
    id: UUID
    last_commit_sha: Optional[str] = None
    last_commit_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    sync_status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Repository(RepositoryInDBBase):
    pass
