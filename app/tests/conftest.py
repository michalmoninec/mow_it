import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app, db
from app.models.map_model import Maps
from app.models.user_model import UserState
from app.models.game_state_model import GameState


@pytest.fixture
def dirs():
    up = "ArrowUp"
    down = "ArrowDown"
    left = "ArrowLeft"
    right = "ArrowRight"

    return {
        "list": [up, down, left, right],
        "up": up,
        "left": left,
        "down": down,
        "right": right,
    }


@pytest.fixture
def test_db():
    app = create_app("config.TestConfig")

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
