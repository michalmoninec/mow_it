import pytest, json

from app import create_app
from app.models.user_model import UserState


@pytest.fixture
def test_map_data():
    return {
        "name": "test_1",
        "map": {"test_key": "test_value"},
        "level": 1,
    }


@pytest.fixture
def test_user_data():
    return {
        "user_id": "abc",
        "level": 1,
        "achieved_level": 1,
        "score": 0,
        "rounds_won": 0,
        "name": "john doe",
        "game_completed": False,
        "level_completed": False,
        "map": json.dumps({"init_key": "init_value"}),
    }


@pytest.fixture
def test_creation_data(test_map_data):
    return {
        "user_id": "test_1234",
        "level": 999,
        "achieved_level": 1,
        "score": 0,
        "rounds_won": 0,
        "name": "Anonymous",
        "game_completed": False,
        "level_completed": False,
        "map": json.dumps(test_map_data),
    }


@pytest.fixture
def test_user_state(test_db, test_user_data):
    user_state = UserState(**test_user_data)
    test_db.session.add(user_state)
    test_db.session.commit()
    return user_state
