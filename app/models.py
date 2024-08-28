from flask import Response
from sqlalchemy import Text, Column, Integer, String

from app.extensions import db


class UserState(db.Model):
    __tablename__ = "user_state"
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(String, nullable=False)
    level = Column(Integer)
    achieved_level = Column(Integer)
    score = Column(Integer)
    map = Column(Text)

    def set_level(self, level: int) -> None:
        self.level = level
        self.map = Maps.query.filter_by(level=level).first().data
        db.session.commit()

    def set_map(self, map: Text) -> None:
        self.map = map
        db.session.commit()

    def increase_level(self):
        self.level += 1
        if self.level > self.achieved_level:
            self.achieved_level = self.level
        self.map = Maps.query.filter_by(level=self.level).first().data

        db.session.commit()


def get_user_by_id(user_id: str) -> any:
    return UserState.query.filter_by(user_id=user_id).first()


def create_user_state(user_id: str) -> None:
    user_state = UserState(user_id=user_id, level=1, achieved_level=1, score=0)
    db.session.add(user_state)
    db.session.commit()


def retrieve_user_state_level(user_id: str) -> int:
    return UserState.query.filter_by(user_id=user_id).first().level


def reset_user_state_level(user_id: str) -> None:
    UserState.query.filter_by(user_id=user_id).first().set_level(level=1)


def set_user_state_level(user_id: str, level: int) -> None:
    user_state = UserState.query.filter_by(user_id=user_id).first()
    user_state.set_level(level)


def advance_user_state_current_level(user_id: str) -> None:
    UserState.query.filter_by(user_id=user_id).first().increase_level()


def get_map_by_user(user_id: str) -> Response:
    return UserState.query.filter_by(user_id=user_id).first().map


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(Integer, primary_key=True)

    name = Column(String)
    start_position = Column(Text)
    level = Column(Integer)
    data = Column(Text)


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
