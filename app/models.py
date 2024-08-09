from .extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Column, Integer, String


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(Integer, primary_key=True)

    name = Column(String)
    data = Column(Text)

    def change_name(self, name):
        self.name = name


class GameState(db.Model):
    __tablename__ = "game_state"
    _id = Column(Integer, primary_key=True)

    room_id = Column(String)
    players = Column(Text)
    map = Column(Text)
    # level = Column(Integer)

    def update_players(self, data):
        self.players = data

    def update_map(self, data):
        self.map = data
