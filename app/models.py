import json

from flask import Response
from sqlalchemy import Text, Column, Integer, String, Boolean, desc
from typing import Tuple

from app.extensions import db
from app.enums import Status
from app.custom_types import NestedDictList

LEVEL_BONUS = 300


class UserState(db.Model):
    __tablename__ = "user_state"
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(String, nullable=False)
    level = Column(Integer)
    achieved_level = Column(Integer)
    score = Column(Integer)
    rounds_won = Column(Integer)
    name = Column(String)
    level_completed = Column(Boolean)
    game_completed = Column(Boolean)
    map = Column(Text)

    def set_level(self, level: int) -> None:
        self.level = level
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

    def set_desired_level(self, desired_level: int) -> None:
        if desired_level <= self.achieved_level:
            self.level = desired_level
        db.session.commit()

    def set_default_state_by_level(self) -> None:
        self.reset_score()
        self.reset_map()
        self.set_level_completed(False)
        self.set_game_completed(False)
        db.session.commit()

    def assign_level_bonus(self) -> None:
        self.set_score(LEVEL_BONUS)


def get_user_by_id(user_id: str) -> UserState:
    return UserState.query.filter_by(user_id=user_id).first()


def create_user_state(user_id: str, level: int = 1) -> None:
    user_state = UserState(user_id=user_id, level=level, achieved_level=1, score=0)
    user_state.set_name("Anonymous")
    user_state.rounds_won = 0
    user_state.set_default_state_by_level()

    db.session.add(user_state)
    db.session.commit()


def advance_user_state_current_level(
    user_id: str, max_level: int | None = None
) -> None:
    if max_level is None:
        max_level = get_max_level_of_maps()
    user_state = get_user_by_id(user_id)
    user_state.increase_level(max_level)
    user_state.reset_map()


def create_user_after_room_join(room_id: str, user_id: str) -> None:
    game_state = GameState.query.filter_by(room_id=room_id).first()
    level = game_state.level

    user_state = get_user_by_id(user_id)
    if user_state is None:
        create_user_state(user_id, level=level)
    else:
        user_state.set_level(game_state.level)
        user_state.set_default_state_by_level()


class Maps(db.Model):
    __tablename__ = "map_data"
    id = Column(Integer, primary_key=True)

    name = Column(String)
    start_position = Column(Text)
    level = Column(Integer)
    data = Column(Text)


def create_maps_database(name: str, map: NestedDictList, level: int) -> None:
    db_map = Maps(name=name, level=level, data=json.dumps(map))
    db.session.add(db_map)
    db.session.commit()


def get_max_level_of_maps() -> int:
    return Maps.query.order_by(desc(Maps.level)).first().level


def get_map_by_level(level: int) -> Text:
    return Maps.query.filter_by(level=level).first().data


class GameState(db.Model):
    __tablename__ = "game_state"
    _id = Column(Integer, primary_key=True)

    room_id = Column(String)

    rounds = Column(Integer)
    current_round = Column(Integer)
    levels_per_round = Column(Integer)
    level = Column(Integer)

    player_1_id = Column(String)
    player_2_id = Column(String)

    p1_rounds_won = Column(Integer)
    p2_rounds_won = Column(Integer)

    status = Column(String)
    winner_id = Column(String)
    map = Column(Text)

    def user_not_in_room(self, user_id: str) -> bool:
        return self.player_1_id != user_id and self.player_2_id != user_id

    def room_is_available(self) -> bool:
        return self.player_1_id == None or self.player_2_id == None

    def add_player(self, user_id: str) -> None:
        if self.player_1_id == None:
            self.player_1_id = user_id
        elif self.player_2_id == None:
            self.player_2_id = user_id

        if self.player_1_id and self.player_2_id:
            print("Passed check for status change.")
            self.status = Status.READY.value

        db.session.commit()

    def set_status(self, status: str) -> None:
        self.status = status
        db.session.commit()

    def get_players(self) -> Tuple[UserState]:
        return get_user_by_id(self.player_1_id), get_user_by_id(self.player_2_id)

    def both_players_completed_level(self) -> bool:
        p1, p2 = self.get_players()
        if p1 and p2:
            return p1.level_completed and p2.level_completed
        return False

    def both_players_completed_game(self) -> bool:
        p1, p2 = self.get_players()
        if p1 and p2:
            return p1.game_completed and p2.game_completed
        return False

    def advance_next_round(self) -> None:
        p1, p2 = self.get_players()

        if self.current_round != self.rounds:
            self.current_round += 1

        self.level += self.levels_per_round
        if self.level > get_max_level_of_maps():
            self.level = get_max_level_of_maps() - self.levels_per_round

        for player in p1, p2:
            player.set_level(self.level)
            player.set_default_state_by_level()

        db.session.commit()

    def final_round(self) -> bool:
        return self.current_round == self.rounds

    def get_max_level(self) -> int:
        return self.level + self.levels_per_round - 1

    def reset_game_state(self) -> None:
        p1, p2 = self.get_players()
        self.level = 1
        self.current_round = 1
        self.p1_rounds_won = 0
        self.p2_rounds_won = 0
        self.winner_id = None
        self.status = Status.READY.value

        for player in p1, p2:
            player.set_level(self.level)
            player.rounds_won = 0
            player.set_default_state_by_level()

        db.session.commit()

    def update_round_winner(self) -> None:
        p1, p2 = self.get_players()
        print(f"p1 score: {p1.score}")
        print(f"p2 score: {p2.score}")
        if p1.score > p2.score:
            p1.rounds_won += 1
        else:
            p2.rounds_won += 1
        db.session.commit()

    def update_game_winner(self) -> None:
        print("Checking who won.")
        p1, p2 = self.get_players()
        if p1.rounds_won > p2.rounds_won:
            self.winner_id = p1.user_id
        else:
            self.winner_id = p2.user_id
        db.session.commit()


def get_game_state_by_room(room_id: str) -> GameState:
    return GameState.query.filter_by(room_id=room_id).first()


def get_game_state_max_level_by_room(room_id: str) -> int:
    return get_game_state_by_room(room_id).get_max_level()


def game_state_advance_ready(room_id: str) -> bool:
    return get_game_state_by_room(room_id).both_players_completed_level()


def game_state_next_round_ready(room_id: str) -> bool:
    return get_game_state_by_room(room_id).both_players_completed_game()


def get_game_state_status(room_id: str) -> str:
    return get_game_state_by_room(room_id).status


def create_multiplayer_game_state(room_id: str, user_id: str) -> None:
    # later will be randomized at creation
    level = 1
    game_state = GameState(room_id=room_id, level=level)
    game_state.map = Maps.query.filter_by(level=level).first().data
    game_state.status = Status.INIT.value
    game_state.rounds = 3
    game_state.levels_per_round = 2
    game_state.current_round = 1
    game_state.p1_rounds_won = 0
    game_state.p2_rounds_won = 0
    game_state.add_player(user_id)

    user_state = get_user_by_id(user_id)
    if user_state is None:
        create_user_state(user_id, level=level)
    else:
        user_state.set_level(game_state.level)
        user_state.rounds_won = 0
        user_state.set_default_state_by_level()

    db.session.add(game_state)
    db.session.commit()
