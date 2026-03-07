from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..models import Inquiry
from ..schemas import InquiryCreate
from .serializer import InquirySerializer

from ..database import session

class InquiryService:
    def __init__(self):
        pass

    async def create(self, inquiry_data: InquiryCreate) -> Inquiry:
        db_inquiry = Inquiry(**inquiry_data.dict())
        session.add(db_inquiry)
        await session.commit()
        await session.refresh(db_inquiry)
        return InquirySerializer().dump(db_inquiry)
