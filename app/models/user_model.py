import uuid

from sqlalchemy import Text, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models.map_model import Maps

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
    game_completed = Column(Boolean)

    level_completed = Column(Boolean)
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

    def add_score(self, diff: int):
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
        self.map = Maps.get_map_by_level(self.level)
        db.session.commit()

    def set_desired_level(self, desired_level: int) -> bool:
        if desired_level <= self.achieved_level:
            self.level = desired_level
            db.session.commit()
            return True
        return False

    def set_default_state_by_level(self) -> None:
        self.reset_score()
        self.reset_map()
        self.set_level_completed(False)
        self.set_game_completed(False)

        db.session.commit()

    def assign_level_bonus(self) -> None:
        self.add_score(LEVEL_BONUS)

    def advance_user_state_current_level(
        user_id: str, max_level: int | None = None
    ) -> None:
        if max_level is None:
            max_level = Maps.get_max_level_of_maps()
        user_state = UserState.get_user_by_id(user_id)
        if user_state.level_completed:
            user_state.increase_level(max_level)
            user_state.reset_map()
            return True
        return False

    @classmethod
    def get_user_by_id(cls, user_id: str) -> "UserState":
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def create_user_state(cls, user_id: str, level: int = 1) -> None:
        user_state = cls(
            user_id=user_id,
            level=level,
            achieved_level=1,
            score=0,
            name="Anonymous",
            rounds_won=0,
        )
        user_state.set_default_state_by_level()

        db.session.add(user_state)
        db.session.commit()
