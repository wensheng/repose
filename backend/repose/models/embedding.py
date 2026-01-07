import uuid

from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func

from repose.db.base_class import Base

class CodeEmbedding(Base):
    __tablename__ = "code_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    file_path = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_hash = Column(String(64))
    
    content = Column(Text, nullable=False)
    # Gemini embedding dimension is 1536 for text-embedding-004
    embedding = mapped_column(Vector(1536))
    
    language = Column(String(50))
    start_line = Column(Integer)
    end_line = Column(Integer)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
