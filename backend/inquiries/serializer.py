from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Inquiry

class InquirySerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Inquiry
        load_instance = True
        include_fk = True
