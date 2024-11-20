import pytest, json

from app import create_app
from app.models.game_state_model import GameState
from app.models.user_model import UserState
from app.scripts.game import create_empty_map, obstacle_col, obstacle_cube

default_obstacles = {
    "level": 1,
    "name": "name01",
    "start": [0, 0],
    "obstacles": obstacle_col(1, 0, 7)
    + obstacle_col(3, 1, 8)
    + obstacle_cube(5, 8, 5, 8),
}

default_map = create_empty_map()
for x, y in default_obstacles["obstacles"]:
    default_map[x][y]["blocker"] = True


@pytest.fixture
def test_user_data(test_map_data):
    return {
        "user_id": "abc",
        "level": 1,
        "achieved_level": 1,
        "score": 0,
        "rounds_won": 0,
        "name": "john doe",
        "game_completed": False,
        "level_completed": False,
        "map": json.dumps(test_map_data["data"]),
    }


@pytest.fixture
def test_creation_data(test_map_data):
    return {
        "user_id": "test_1234",
        "level": 1,
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
        "map": test_map_data["data"],
        "status": "init",
        "rounds": 2,
        "levels_per_round": 3,
        "current_round": 1,
        "p1_rounds_won": 0,
        "p2_rounds_won": 0,
    }


@pytest.fixture
def test_user(test_db, test_user_data):
    user_state = UserState(**test_user_data)
    test_db.session.add(user_state)
    test_db.session.commit()
    return user_state


@pytest.fixture
def test_game(test_db, game_data):
    game_state = GameState(**game_data)
    test_db.session.add(game_state)
    test_db.session.commit()
    return game_state


@pytest.fixture
def p1_test(test_db, test_game):
    p1 = UserState(user_id="id1")
    test_db.session.add(p1)
    test_db.session.commit()
    return p1


@pytest.fixture
def p2_test(test_db, test_game):
    p2 = UserState(user_id="id2")
    test_db.session.add(p2)
    test_db.session.commit()
    return p2


@pytest.fixture
def apply_validation():
    def wrapper(decorator, decorator_args, func):
        actual_decorator = decorator(decorator_args)
        return actual_decorator(func)

    return wrapper
