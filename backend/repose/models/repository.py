from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from repose.db.base_class import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(20), nullable=False)  # 'github', 'gitlab'
    org_name = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    full_name = Column(String(512), nullable=False, unique=True)
    default_branch = Column(String(100), default="main")
    
    # Sync tracking
    last_commit_sha = Column(String(40))
    last_commit_at = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))
    sync_status = Column(String(20), default="pending")
    
    # Configuration
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
