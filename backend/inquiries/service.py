import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..models import Inquiry
from ..schemas import InquiryCreate
from .serializer import InquirySerializer
from .notification_service import NotificationService

from ..database import session

class InquiryService:
    def __init__(self):
        self.notification_service = NotificationService()

    async def create(self, inquiry_data: InquiryCreate) -> Inquiry:
        db_inquiry = Inquiry(**inquiry_data.dict())
        session.add(db_inquiry)
        await session.commit()
        await session.refresh(db_inquiry)
        result = InquirySerializer().dump(db_inquiry)

        # Fire-and-forget — returns response immediately, email sends in background
        asyncio.create_task(self.notification_service.send_email(result))

        return result
