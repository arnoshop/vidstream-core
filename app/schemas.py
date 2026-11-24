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


class PreRollAdCreate(BaseModel):
    campaign_name: str
    ad_video_url: str
    target_click_url: str
    skip_after_seconds: int = 5

    @field_validator("campaign_name")
    @classmethod
    def check_campaign_name(cls, value):
        cleaned_name = value.strip()
        if len(cleaned_name) < 2:
            raise ValueError("campaign_name must be at least 2 characters")
        return cleaned_name

    @field_validator("ad_video_url")
    @classmethod
    def check_ad_video_url(cls, value):
        cleaned_url = value.strip()
        if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
            raise ValueError("ad_video_url must start with http:// or https://")
        return cleaned_url

    @field_validator("target_click_url")
    @classmethod
    def check_target_click_url(cls, value):
        cleaned_url = value.strip()
        if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
            raise ValueError("target_click_url must start with http:// or https://")
        return cleaned_url

    @field_validator("skip_after_seconds")
    @classmethod
    def check_skip_seconds(cls, value):
        if value < 0:
            raise ValueError("skip_after_seconds cannot be negative")
        if value > 30:
            raise ValueError("skip_after_seconds cannot exceed 30 seconds")
        return value


class PreRollAdOut(BaseModel):
    id: int
    campaign_name: str
    ad_video_url: str
    target_click_url: str
    skip_after_seconds: int
    impressions_count: int
    clicks_count: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)