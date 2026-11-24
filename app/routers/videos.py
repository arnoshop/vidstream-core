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