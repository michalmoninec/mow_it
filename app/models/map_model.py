import json, uuid


from sqlalchemy import Text, Column, Integer, String, desc
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.custom_types import NestedDictList


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)
    start_position = Column(Text)
    level = Column(Integer)
    data = Column(Text)

    @classmethod
    def create_maps_database(cls, name: str, map: NestedDictList, level: int) -> None:
        db_map = cls(name=name, level=level, data=json.dumps(map))
        db.session.add(db_map)
        db.session.commit()

    @classmethod
    def get_max_level_of_maps(cls) -> int:
        return cls.query.order_by(desc(cls.level)).first().level

    @classmethod
    def get_map_by_level(cls, level: int) -> Text:
        return cls.query.filter_by(level=level).first().data

    @classmethod
    def is_map_table_empty(cls):
        if db.session.query(cls).first() == None:
            return True
        return False
