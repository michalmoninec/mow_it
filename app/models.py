import json

from flask import Response
from sqlalchemy import Text, Column, Integer, String, Boolean
from typing import List

from app.extensions import db
from app.enums import Status

MAX_LEVEL = 3


class UserState(db.Model):
    __tablename__ = "user_state"
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(String, nullable=False)
    level = Column(Integer)
    achieved_level = Column(Integer)
    score = Column(Integer)
    name = Column(String)
    level_completed = Column(Boolean)
    game_completed = Column(Boolean)
    map = Column(Text)

    def set_level(self, level: int) -> None:
        self.level = level
        self.map = Maps.query.filter_by(level=level).first().data
        db.session.commit()

    def set_map(self, map: Text) -> None:
        self.map = map
        db.session.commit()

    def increase_level(self, max_level: int):
        self.level += 1
        if self.level > max_level:
            self.level = max_level
        if self.level > self.achieved_level:
            self.achieved_level = self.level
        self.level_completed = False
        self.game_completed = False
        # self.map = Maps.query.filter_by(level=self.level).first().data

        db.session.commit()

    def set_name(self, name: str):
        self.name = name
        db.session.commit()

    def set_score(self, diff: int):
        self.score += diff
        db.session.commit()

    def reset_score(self):
        self.score = 0
        db.session.commit()

    def set_level_completed(self, value: bool):
        self.level_completed = value
        db.session.commit()

    def set_game_completed(self, value: bool):
        self.game_completed = value
        db.session.commit()

    def reset_map(self):
        self.map = get_map_by_level(self.level)
        db.session.commit()


def get_user_by_id(user_id: str) -> any:
    return UserState.query.filter_by(user_id=user_id).first()


def set_user_name(user_id: str, name: str) -> None:
    user_state = UserState.query.filter_by(user_id=user_id).first()
    user_state.set_name(name=name)


def set_user_score(user_id: str, diff: int) -> None:
    user_state = get_user_by_id(user_id=user_id)
    user_state.set_score(diff=diff)


def create_user_state(user_id: str, level=1) -> None:
    user_state = UserState(user_id=user_id, level=level, achieved_level=1, score=0)
    user_state.set_level(level)
    user_state.set_name("Anonymous")
    user_state.level_completed = False
    user_state.game_completed = False

    db.session.add(user_state)
    db.session.commit()


def retrieve_user_state_level(user_id: str) -> int:
    return UserState.query.filter_by(user_id=user_id).first().level


def reset_user_state_level(user_id: str) -> None:
    UserState.query.filter_by(user_id=user_id).first().set_level(level=1)


def set_user_state_level(user_id: str, level: int) -> None:
    user_state = UserState.query.filter_by(user_id=user_id).first()
    user_state.set_level(level)


def advance_user_state_current_level(user_id: str, max_level: int) -> None:
    UserState.query.filter_by(user_id=user_id).first().increase_level(max_level)


def get_map_by_user(user_id: str) -> Response:
    return UserState.query.filter_by(user_id=user_id).first().map


def get_map_by_level(level: int) -> Response:
    return Maps.query.filter_by(level=level).first().data


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(Integer, primary_key=True)

    name = Column(String)
    start_position = Column(Text)
    level = Column(Integer)
    data = Column(Text)


def create_multiplayer_game_state(room_id: str, player_id: str) -> None:
    # later will be randomized at creation
    level = 1
    game_state = GameState(room_id=room_id, level=level)
    game_state.map = Maps.query.filter_by(level=level).first().data
    game_state.status = Status.INIT.value
    game_state.rounds = 2
    game_state.current_round = 1
    game_state.add_player(player_id)

    create_user_state(user_id=player_id, level=level)

    db.session.add(game_state)
    db.session.commit()


def create_user_after_room_join(room_id: str, player_id: str) -> None:
    game_state = GameState.query.filter_by(room_id=room_id).first()
    level = game_state.level

    create_user_state(user_id=player_id, level=level)


class GameState(db.Model):
    __tablename__ = "game_state"
    _id = Column(Integer, primary_key=True)

    room_id = Column(String)

    rounds = Column(Integer)
    current_round = Column(Integer)
    levels_per_round = Column(Integer)

    player_1_id = Column(String)
    player_2_id = Column(String)

    p1_rounds_won = Column(Integer)
    p2_rounds_won = Column(Integer)

    status = Column(String)
    level = Column(String)
    winner_id = Column(String)
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

    def set_status(self, status: str) -> None:
        self.status = status
        db.session.commit()

    def get_players(self) -> List[Maps]:
        return get_user_by_id(self.player_1_id), get_user_by_id(self.player_2_id)

    def both_players_completed_level(self):
        p1, p2 = self.get_players()
        if p1 and p2:
            return p1.level_completed and p2.level_completed
        return False

    def both_players_completed_game(self):
        p1, p2 = self.get_players()
        if p1 and p2:
            return p1.game_completed and p2.game_completed
        return False

    def advance_next_round(self) -> None:
        p1, p2 = self.get_players()

        if self.current_round != self.rounds:
            self.current_round += 1

        self.level = 3

        for player in p1, p2:
            player.set_level(self.level)
            player.set_level_completed(False)
            player.set_game_completed(False)
            player.reset_score()

        db.session.commit()

    def final_round(self) -> bool:
        return self.current_round == self.rounds


def get_game_state_by_room(room_id: str) -> any:
    return GameState.query.filter_by(room_id=room_id).first()


def get_game_state_max_level_by_room(room_id: str) -> int:
    return int(get_game_state_by_room(room_id).level) + 1
