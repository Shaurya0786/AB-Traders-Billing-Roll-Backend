from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import SiteStatistic

class StatsSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = SiteStatistic
        load_instance = True
