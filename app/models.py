from .extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Column, Integer, String


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(Text)
