import pytest, json

from app import create_app
from app.models.game_state_model import GameState
from app.models.user_model import UserState


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
def game_method_create(test_map_data):
    return {
        "level": 1,
        "map": test_map_data["map"],
        "status": "init",
        "rounds": 2,
        "levels_per_round": 3,
        "current_round": 1,
        "p1_rounds_won": 0,
        "p2_rounds_won": 0,
    }


@pytest.fixture
def test_user_state(test_db, test_user_data):
    user_state = UserState(**test_user_data)
    test_db.session.add(user_state)
    test_db.session.commit()
    return user_state


@pytest.fixture
def game_state(test_db, game_data):
    game_state = GameState(**game_data)
    test_db.session.add(game_state)
    test_db.session.commit()
    return game_state


@pytest.fixture
def p1_test(test_db, game_state):
    p1 = UserState(user_id="id1")
    test_db.session.add(p1)
    test_db.session.commit()
    return p1


@pytest.fixture
def p2_test(test_db, game_state):
    p2 = UserState(user_id="id2")
    test_db.session.add(p2)
    test_db.session.commit()
    return p2
