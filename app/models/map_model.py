import json, uuid


from sqlalchemy import Text, Column, Integer, String, desc
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.types_validation import NestedDictList


class Maps(db.Model):
    """
    Class, that handles ORM with map_data table in sqlalchemy.
    """

    __tablename__ = "map_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)
    start_position = Column(Text)
    level = Column(Integer)
    data = Column(Text)

    @classmethod
    def create_maps_database(cls, name: str, map: NestedDictList, level: int) -> None:
        """
        Creates, adds and commit new Maps object into database based on provided:
        name, map, level.
        """
        db_map = cls(name=name, level=level, data=json.dumps(map))
        db.session.add(db_map)
        db.session.commit()

    @classmethod
    def get_max_level_of_maps(cls) -> int:
        """
        Returns maximal level of Maps table.
        If there are no Maps, returns None.
        """
        max_level_map = cls.query.order_by(desc(cls.level)).first()
        if max_level_map:
            return max_level_map.level
        return None

    @classmethod
    def get_map_by_level(cls, level: int) -> Text:
        """
        Returns Maps.data for Maps object with same level.
        If there is no match, returns None.
        """
        map = cls.query.filter_by(level=level).first()
        if map:
            return map.data
        return None

    @classmethod
    def is_map_table_empty(cls):
        """
        Chekcks, if there are some rows in Maps table.
        Returns True if there are some, otherwise False.
        """
        if db.session.query(cls).first() == None:
            return True
        return False
