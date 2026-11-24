import secrets
from fastapi import Header, HTTPException, status
from app.config import settings


def verify_admin_key(x_admin_key: str = Header(default=None)):
    configured_key = settings.admin_api_key

    if configured_key is None or configured_key.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin API key is not configured on the server"
        )

    if x_admin_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Admin-Key header"
        )

    provided_key = x_admin_key.strip()
    if provided_key == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty X-Admin-Key header"
        )

    is_match = secrets.compare_digest(provided_key, configured_key)
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin key"
        )

    return True