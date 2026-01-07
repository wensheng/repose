from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from repose.db.base_class import Base

class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # 'counter', 'gauge', 'histogram'
    value = Column(Float, nullable=False)
    labels = Column(JSON, default={})
    metadata_ = Column("metadata", JSON, default={}) # 'metadata' is reserved in Base sometimes, using metadata_ mapped to "metadata"
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
