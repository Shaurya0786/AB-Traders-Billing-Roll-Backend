from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Product

class ProductSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
