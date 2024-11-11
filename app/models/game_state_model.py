import uuid

from flask import Response
from sqlalchemy import Text, Column, Integer, String, Boolean, desc
from sqlalchemy.dialects.postgresql import UUID
from typing import Tuple

from app.extensions import db
from app.enums import Status
from app.custom_types import NestedDictList

from app.models.user_model import UserState, Maps

LEVEL_BONUS = 300


class GameState(db.Model):
    __tablename__ = "game_state"
    id = Column(Integer, primary_key=True)

    room_id = Column(String)

    rounds = Column(Integer)
    current_round = Column(Integer)
    levels_per_round = Column(Integer)
    level = Column(Integer)
    default_level = Column(Integer)

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
            self.status = Status.READY.value

        db.session.commit()

    def del_player(self, user_id: str):
        if self.player_1_id == user_id:
            self.player_1_id = None
        elif self.player_2_id == user_id:
            self.player_2_id = None

        if self.player_1_id is None and self.player_2_id is None:
            game_state = GameState.get_game_state_by_room(self.room_id)
            db.session.delete(game_state)

        db.session.commit()

    def set_status(self, status: str) -> None:
        self.status = status
        db.session.commit()

    def update_status(self):
        p1, p2 = self.get_players()
        if p1 and p2:
            self.status = Status.READY.value
            if p1.game_completed and p2.game_completed:
                self.status = Status.FINISHED.value
        else:
            self.status = Status.JOIN_WAIT.value

        db.session.commit()

    def get_players(self) -> Tuple[UserState, UserState]:
        return UserState.get_user_by_id(self.player_1_id), UserState.get_user_by_id(
            self.player_2_id
        )

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
        if self.level > Maps.get_max_level_of_maps():
            self.level = Maps.get_max_level_of_maps() - self.levels_per_round

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
            if player:
                player.set_level(self.level)
                player.rounds_won = 0
                player.set_default_state_by_level()

        db.session.commit()

    def update_round_winner(self) -> None:
        p1, p2 = self.get_players()
        if p1.score > p2.score:
            p1.rounds_won += 1
        elif p1.score < p2.score:
            p2.rounds_won += 1

        db.session.commit()

    def update_game_winner(self) -> None:
        p1, p2 = self.get_players()
        if p1.rounds_won > p2.rounds_won:
            self.winner_id = p1.user_id
        elif p1.rounds_won < p2.rounds_won:
            self.winner_id = p2.user_id
        else:
            self.winner_id = None
        db.session.commit()

    def get_game_state_max_level_by_room(room_id: str) -> int:
        return GameState.get_game_state_by_room(room_id).get_max_level()

    def game_state_advance_ready(room_id: str) -> bool:
        return GameState.get_game_state_by_room(room_id).both_players_completed_level()

    def game_state_next_round_ready(room_id: str) -> bool:
        return GameState.get_game_state_by_room(room_id).both_players_completed_game()

    def get_game_state_status(room_id: str) -> str:
        return GameState.get_game_state_by_room(room_id).status

    @classmethod
    def get_game_state_by_room(cls, room_id: str) -> "GameState":
        return cls.query.filter_by(room_id=room_id).first()

    @classmethod
    def create_multiplayer_game_state(cls, room_id: str) -> None:
        level = 1
        game_state = cls(room_id=room_id, level=level)
        game_state.map = Maps.query.filter_by(level=level).first().data
        game_state.status = Status.INIT.value
        game_state.rounds = 2
        game_state.levels_per_round = 3
        game_state.current_round = 1
        game_state.p1_rounds_won = 0
        game_state.p2_rounds_won = 0

        db.session.add(game_state)
        db.session.commit()

    @classmethod
    def create_user_after_room_join(cls, room_id: str, user_id: str) -> None:
        game_state = cls.query.filter_by(room_id=room_id).first()
        level = game_state.level

        user_state = UserState.get_user_by_id(user_id)
        if user_state is None:
            UserState.create_user_state(user_id, level=level)
        else:
            user_state.set_level(game_state.level)
            user_state.rounds_won = 0
            user_state.set_default_state_by_level()
