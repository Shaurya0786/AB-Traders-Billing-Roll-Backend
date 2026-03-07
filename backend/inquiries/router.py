from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import InquiryService
from ..schemas import InquiryCreate

router = APIRouter(
    prefix="/inquiries",
    tags=["inquiries"]
)

@router.post("", status_code=201)
async def create_inquiry(inquiry: InquiryCreate):
    """Create a new inquiry or quote request."""
    service = InquiryService()
    return await service.create(inquiry)
