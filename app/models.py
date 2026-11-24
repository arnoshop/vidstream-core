from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


def get_utc_now():
    current_time = datetime.now(timezone.utc)
    return current_time


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    stream_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)