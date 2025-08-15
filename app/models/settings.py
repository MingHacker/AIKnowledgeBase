from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, CheckConstraint, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_model = Column(String(100), default="gpt-3.5-turbo")
    max_tokens = Column(Integer, default=1000)
    temperature = Column(DECIMAL(3, 2), default=0.7)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    default_document_filter = Column(JSON, default=lambda: [])
    ui_preferences = Column(JSON, default=lambda: {})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")

    __table_args__ = (
        CheckConstraint("temperature >= 0 AND temperature <= 2", name="check_temperature_range"),
    )