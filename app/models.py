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
    status = Column(String)
    level = Column(String)
    winner_id = Column(String)

    player_1_id = Column(String)
    player_2_id = Column(String)

    player_1_map = Column(Text)
    player_2_map = Column(Text)

    player_1_pos = Column(Text)
    player_2_pos = Column(Text)

    player_1_score = Column(Integer)
    player_2_score = Column(Integer)
    map = Column(Text)

    def add_player(self, player_id):
        if self.player_1_id == None:
            self.player_1_id = player_id
            return self.player_1_id
        elif self.player_2_id == None:
            self.player_2_id = player_id
            return self.player_2_id
        else:
            return None
