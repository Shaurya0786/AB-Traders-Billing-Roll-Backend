from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import StatsService

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("")
async def get_stats():
    """Get site statistics."""
    service = StatsService()
    return await service.get_all()
