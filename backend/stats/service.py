from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..models import SiteStatistic
from .serializer import StatsSerializer

from ..database import session

class StatsService:
    def __init__(self):
        pass

    async def get_all(self):
        result = await session.execute(select(SiteStatistic))
        stats = result.scalars().all()
        return StatsSerializer(many=True).dump(stats)
