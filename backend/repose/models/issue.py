from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from sqlalchemy.sql import func
from repose.db.base_class import Base

class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TriageStatus(str, enum.Enum):
    PENDING = "pending"
    TRIAGED = "triaged"
    IGNORED = "ignored"

class Issue(Base):
    __tablename__ = "issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    github_id = Column(Integer, nullable=True) # ID from GitHub
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=True)
    state = Column(String, nullable=False) # open, closed
    html_url = Column(String, nullable=False)
    
    # Triage Fields (LLM populated)
    triage_status = Column(String, default=TriageStatus.PENDING)
    priority = Column(String, nullable=True)
    tags = Column(JSON, nullable=True) # List of strings
    summary = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
