import random
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


@router.get("/serve", response_model=PreRollAdOut)
def serve_random_ad(db: Session = Depends(get_db)):
    active_ads = (
        db.query(PreRollAd)
        .filter(PreRollAd.is_active == True)
        .all()
    )

    if len(active_ads) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active preroll ads available"
        )

    last_index = len(active_ads) - 1
    chosen_index = random.randint(0, last_index)
    selected_ad = active_ads[chosen_index]

    if selected_ad.impressions_count is None:
        selected_ad.impressions_count = 0

    selected_ad.impressions_count = selected_ad.impressions_count + 1

    try:
        db.commit()
        db.refresh(selected_ad)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ad impressions"
        )

    return selected_ad