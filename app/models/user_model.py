import uuid

from sqlalchemy import Text, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models.map_model import Maps

LEVEL_BONUS = 300


class UserState(db.Model):
    """Class, that handles ORM with user_state table in sqlalchemy."""

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
        """Sets level to provided value and commits it to db."""
        self.level = level
        db.session.commit()

    def set_map(self, map: Text) -> None:
        """Sets map to provided value and commits it to db."""
        self.map = map
        db.session.commit()

    def increase_level(self, max_level: int):
        """Increases level by value of 1 with boundary of max level.
        Resets level and game completion.
        """
        self.level += 1
        if self.level > max_level:
            self.level = max_level
        if self.level > self.achieved_level:
            self.achieved_level = self.level
        self.level_completed = False
        self.game_completed = False

        db.session.commit()

    def set_name(self, name: str):
        """Sets and commit name to db."""
        self.name = name
        db.session.commit()

    def add_score(self, diff: int):
        """Adds score with provided diff and commits to db."""
        self.score += diff
        db.session.commit()

    def reset_score(self):
        """Resets score to 0 and commits to db."""
        self.score = 0
        db.session.commit()

    def set_level_completed(self, value: bool):
        """Sets level completion and commits to db."""
        self.level_completed = value
        db.session.commit()

    def set_game_completed(self, value: bool):
        """Sets game completion and commits to db."""
        self.game_completed = value
        db.session.commit()

    def reset_map(self):
        """Resets map to default by level and commits to db."""
        self.map = Maps.get_map_by_level(self.level)
        db.session.commit()

    def set_desired_level(self, desired_level: int) -> bool:
        """Sets desired level with boundary of achieved level and commits to db.
        If in boundary, returns True, otherwise returns False.
        """
        if desired_level <= self.achieved_level:
            self.level = desired_level
            db.session.commit()
            return True
        return False

    def set_default_state_by_level(self) -> None:
        """Sets default state for:
        - Score.
        - Map.
        - Level completion.
        - Game completion.
        And commits to db.
        """
        self.reset_score()
        self.reset_map()
        self.set_level_completed(False)
        self.set_game_completed(False)

        db.session.commit()

    def assign_level_bonus(self) -> None:
        """Assigns level bonus."""
        self.add_score(LEVEL_BONUS)

    def to_dict(self, client_key: str) -> dict:
        """Return dictionary represantation of UserModel."""
        user_dict = {
            key: value
            for key, value in vars(self).items()
            if key != "_sa_instance_state"
        }
        user_dict["key"] = client_key
        return user_dict

    @classmethod
    def advance_user_state_current_level(
        cls, user_id: str, max_level: int = None
    ) -> bool:
        """Advances to next level.
        If max level is not provided, it is set up as maximum level of all Maps.
        Gets UserState by provided user_id.
        If UserState is not None and level is completed, then it increases level
        with boundary of max level.
        Then map is reset by the new level.
        If correct advance and UserState exists, returns True, otherwise returns False.
        """
        if max_level is None:
            max_level = Maps.get_max_level_of_maps()

        user_state = cls.get_user_by_id(user_id)
        if user_state and user_state.level_completed:
            user_state.increase_level(max_level)
            user_state.reset_map()
            return True
        return False

    @classmethod
    def get_user_by_id(cls, user_id: str) -> "UserState":
        """Returns UserState with matching user_id.
        If not found, returns None.
        If multiple matches, returns first.
        """
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def create_user_state(cls, user_id: str, level: int = 1) -> None:
        """Creates new UserState model with provided user_id and level.
        Sets default state for new UserState and commits to db.
        """
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
