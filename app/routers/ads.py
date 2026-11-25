import random
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PreRollAd
from app.schemas import PreRollAdCreate, PreRollAdOut
from app.security import verify_admin_key
from app.storage import save_uploaded_video
from app.utils import build_vast_xml

router = APIRouter(
    prefix="/ads",
    tags=["Ads"]
)


@router.get(
    "/",
    response_model=List[PreRollAdOut],
    dependencies=[Depends(verify_admin_key)]
)
def list_preroll_ads(db: Session = Depends(get_db)):
    query = db.query(PreRollAd)
    query = query.order_by(PreRollAd.created_at.desc())
    ads_list = query.all()
    return ads_list


@router.post(
    "/",
    response_model=PreRollAdOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_key)]
)
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


@router.post(
    "/upload",
    response_model=PreRollAdOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_key)]
)
def upload_preroll_ad(
    campaign_name: str = Form(...),
    target_click_url: str = Form(...),
    skip_after_seconds: int = Form(5),
    ad_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    cleaned_name = campaign_name.strip()
    if len(cleaned_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="campaign_name must be at least 2 characters"
        )

    cleaned_click_url = target_click_url.strip()
    if not cleaned_click_url.startswith("http://") and not cleaned_click_url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_click_url must start with http:// or https://"
        )

    if skip_after_seconds < 0 or skip_after_seconds > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip_after_seconds must be between 0 and 30"
        )

    saved_ad_url = save_uploaded_video(ad_file, "ads")

    new_ad = PreRollAd(
        campaign_name=cleaned_name,
        ad_video_url=saved_ad_url,
        target_click_url=cleaned_click_url,
        skip_after_seconds=skip_after_seconds
    )

    try:
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded preroll ad in database"
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


@router.get("/vast.xml")
def get_vast_xml(request: Request, db: Session = Depends(get_db)):
    empty_vast = '<?xml version="1.0" encoding="UTF-8"?>\n<VAST version="3.0"></VAST>'

    active_ads = (
        db.query(PreRollAd)
        .filter(PreRollAd.is_active == True)
        .all()
    )

    if len(active_ads) == 0:
        return Response(content=empty_vast, media_type="application/xml")

    last_index = len(active_ads) - 1
    chosen_index = random.randint(0, last_index)
    selected_ad = active_ads[chosen_index]

    if selected_ad.impressions_count is None:
        selected_ad.impressions_count = 0

    selected_ad.impressions_count = selected_ad.impressions_count + 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        return Response(content=empty_vast, media_type="application/xml")

    final_media_url = selected_ad.ad_video_url
    if final_media_url.startswith("/"):
        base_host = str(request.base_url).rstrip("/")
        final_media_url = base_host + final_media_url

    xml_content = build_vast_xml(
        ad_id=selected_ad.id,
        campaign_name=selected_ad.campaign_name,
        video_url=final_media_url,
        click_url=selected_ad.target_click_url,
        skip_seconds=selected_ad.skip_after_seconds
    )

    return Response(content=xml_content, media_type="application/xml")


@router.post("/{ad_id}/click", response_model=PreRollAdOut)
def track_ad_click(ad_id: int, db: Session = Depends(get_db)):
    ad_item = (
        db.query(PreRollAd)
        .filter(PreRollAd.id == ad_id)
        .first()
    )

    if ad_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad campaign not found"
        )

    if ad_item.clicks_count is None:
        ad_item.clicks_count = 0

    ad_item.clicks_count = ad_item.clicks_count + 1

    try:
        db.commit()
        db.refresh(ad_item)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ad click count"
        )

    return ad_item


@router.delete("/{ad_id}", dependencies=[Depends(verify_admin_key)])
def delete_preroll_ad(ad_id: int, db: Session = Depends(get_db)):
    ad_item = (
        db.query(PreRollAd)
        .filter(PreRollAd.id == ad_id)
        .first()
    )

    if ad_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad campaign not found"
        )

    try:
        db.delete(ad_item)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preroll ad from database"
        )

    result = {}
    result["status"] = "deleted"
    result["ad_id"] = ad_id
    return result