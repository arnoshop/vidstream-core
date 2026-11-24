from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PreRollAd
from app.schemas import PreRollAdCreate, PreRollAdOut

router = APIRouter(
    prefix="/ads",
    tags=["Ads"]
)


@router.post("/", response_model=PreRollAdOut, status_code=status.HTTP_201_CREATED)
def create_preroll_ad(payload: PreRollAdCreate, db: Session = Depends(get_db)):
    new_ad = PreRollAd(
        campaign_name=payload.campaign_name,
        ad_video_url=payload.ad_video_url,
        target_click_url=payload.target_click_url,
        skip_after_seconds=payload.skip_after_seconds
    )

    try:
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save preroll ad in database"
        )

    return new_ad