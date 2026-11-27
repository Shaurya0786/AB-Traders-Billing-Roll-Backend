import hmac
import os

from fastapi import Header, HTTPException


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    """Product changes need the X-Admin-Key header to match ADMIN_API_KEY. With no ADMIN_API_KEY set, they are off."""
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=403, detail="Product changes are switched off on this server.")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=401, detail="Missing or wrong admin key.")
