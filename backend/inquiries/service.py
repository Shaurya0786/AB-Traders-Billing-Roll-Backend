import asyncio

from sqlalchemy import select

from ..database import session
from ..models import Inquiry, InquiryItem, Product
from ..schemas import InquiryCreate
from .notification_service import NotificationService
from .serializer import InquirySerializer


class InquiryService:
    def __init__(self):
        self.notification_service = NotificationService()

    async def create(self, inquiry_data: InquiryCreate) -> dict:
        db_inquiry = Inquiry(**inquiry_data.model_dump(exclude={"items"}))
        session.add(db_inquiry)
        await session.flush()  # gives the enquiry its id for the item rows

        # each cart product under the name it has now; a product removed meanwhile keeps its slug as the name
        slugs = [it.product_slug for it in inquiry_data.items]
        names = {}
        if slugs:
            rows = await session.execute(select(Product.slug, Product.name).where(Product.slug.in_(slugs)))
            names = dict(rows.all())
        items = [InquiryItem(inquiry_id=db_inquiry.id, product_slug=it.product_slug,
                             product_name=names.get(it.product_slug, it.product_slug), boxes=it.boxes)
                 for it in inquiry_data.items]
        session.add_all(items)

        await session.commit()
        await session.refresh(db_inquiry)
        result = InquirySerializer().dump(db_inquiry)
        result["items"] = [{"product_slug": i.product_slug, "product_name": i.product_name, "boxes": i.boxes} for i in items]

        # Fire-and-forget — returns response immediately, email sends in background
        asyncio.create_task(self.notification_service.send_email(result))

        return result
