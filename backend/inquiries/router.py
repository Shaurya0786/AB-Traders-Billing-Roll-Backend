import os
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request

from ..schemas import InquiryCreate
from .service import InquiryService

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


class RateLimiter:
    """At most `limit` enquiries per visitor (IP address) in `window` seconds, kept in memory.
    Enough to stop a script flooding the inbox; it resets when the server restarts."""

    def __init__(self, limit: int, window: float):
        self.limit, self.window = limit, window
        self.hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now, q = time.monotonic(), self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True

    def reset(self) -> None:
        self.hits.clear()


limiter = RateLimiter(int(os.getenv("INQUIRY_RATE_LIMIT", "5")), float(os.getenv("INQUIRY_RATE_WINDOW", "600")))


def client_ip(request: Request) -> str:
    # behind Render's or Vercel's proxy the visitor's address is the first one in X-Forwarded-For
    forwarded = request.headers.get("x-forwarded-for")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")


@router.post("", status_code=201)
async def create_inquiry(inquiry: InquiryCreate, request: Request):
    """Create a new inquiry or quote request."""
    if not limiter.allow(client_ip(request)):
        raise HTTPException(status_code=429, detail="Too many enquiries from this connection. Please call or WhatsApp us.")
    return await InquiryService().create(inquiry)
