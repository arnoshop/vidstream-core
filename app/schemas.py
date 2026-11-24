from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    stream_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int = 0

    @field_validator("title")
    @classmethod
    def check_title(cls, value):
        cleaned_title = value.strip()
        if len(cleaned_title) < 3:
            raise ValueError("title must be at least 3 characters")
        return cleaned_title

    @field_validator("stream_url")
    @classmethod
    def check_stream_url(cls, value):
        cleaned_url = value.strip()
        if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
            raise ValueError("stream_url must start with http:// or https://")
        return cleaned_url


class VideoOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    stream_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    views_count: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)