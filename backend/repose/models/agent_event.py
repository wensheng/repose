from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from repose.db.base_class import Base

class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(String, nullable=False) # e.g., "commit", "pr", "comment"
    agent_name = Column(String, nullable=True)  # e.g., "Copilot", "Sweep"
    confidence = Column(Float, default=0.0)
    
    source_ref = Column(String) # commit hash or PR number
    description = Column(Text)
    
    is_reviewed = Column(Boolean, default=False)
    review_status = Column(String) # "approved", "rejected", "pending"
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
