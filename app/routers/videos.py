from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video
from app.schemas import VideoCreate, VideoOut
from app.utils import generate_slug

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


@router.post("/", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
def create_video(payload: VideoCreate, db: Session = Depends(get_db)):
    slug_value = generate_slug(payload.title)

    existing = db.query(Video).filter(Video.slug == slug_value).first()
    if existing is not None:
        slug_value = generate_slug(payload.title)

    new_video = Video(
        title=payload.title,
        slug=slug_value,
        description=payload.description,
        stream_url=payload.stream_url,
        thumbnail_url=payload.thumbnail_url,
        duration_seconds=payload.duration_seconds
    )

    try:
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save video in database"
        )

    return new_video


@router.get("/", response_model=List[VideoOut])
def list_videos(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    if skip < 0:
        skip = 0

    if limit < 1:
        limit = 20

    if limit > 100:
        limit = 100

    query = db.query(Video)
    query = query.filter(Video.is_active == True)
    query = query.order_by(Video.created_at.desc())
    videos_list = query.offset(skip).limit(limit).all()

    return videos_list


@router.get("/{slug}", response_model=VideoOut)
def get_video_by_slug(slug: str, db: Session = Depends(get_db)):
    cleaned_slug = slug.strip()

    video_item = (
        db.query(Video)
        .filter(Video.slug == cleaned_slug)
        .filter(Video.is_active == True)
        .first()
    )

    if video_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video_item.views_count is None:
        video_item.views_count = 0

    video_item.views_count = video_item.views_count + 1

    try:
        db.commit()
        db.refresh(video_item)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update video view count"
        )

    return video_item