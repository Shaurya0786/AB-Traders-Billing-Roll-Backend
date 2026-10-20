import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException

_ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def require_admin(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> None:
    """Validate the X-API-Key header against ADMIN_API_KEY from env.

    - 503 if the server is misconfigured (env var missing).
    - 401 if the header is missing or wrong (same message either way).
    """
    if not _ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin auth not configured")
    if not x_api_key or not hmac.compare_digest(
        x_api_key.encode("utf-8"), _ADMIN_API_KEY.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
