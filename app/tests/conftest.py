import pytest, json

from flask_socketio import SocketIO

from app import db, test_app

from app.scripts.game import create_empty_map, obstacle_col, obstacle_cube
from app.socket import configure_socketio
from app.models.map_model import Maps
from app.models.user_model import UserState
from app.models.game_state_model import GameState


default_obstacles = {
    "level": 1,
    "name": "name_conftest",
    "start": [0, 0],
    "obstacles": obstacle_col(0, 3, 10) + obstacle_cube(1, 10, 0, 10),
}

default_map = create_empty_map()
default_map[0][0]["active"] = True
default_map[0][0]["visited"] = True
for x, y in default_obstacles["obstacles"]:
    default_map[x][y]["blocker"] = True
    default_map[x][y]["visited"] = True


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
def test_db(client):
    with client.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    app = test_app()
    app.testing = True
    with app.app_context():
        yield app


@pytest.fixture
def test_client(client):
    with client.test_client() as test_client:
        yield test_client


@pytest.fixture
def socket_client(client):
    socketio = SocketIO(client, manage_session=False)
    configure_socketio(socketio)
    socketio_test_client = socketio.test_client(client)
    return socketio_test_client


@pytest.fixture
def test_user(test_db, test_user_data):
    user_state = UserState(**test_user_data)
    test_db.session.add(user_state)
    test_db.session.commit()
    return user_state


@pytest.fixture
def mock_method(mocker, request):
    """
    Mocks method of provided object.
    Possiblity to mock return_value, side_effect.
    After use, stops mock.
    """

    def mock_wrapper(obj, class_method, return_value=None, side_effect=None):
        mock_method = mocker.patch.object(
            obj, class_method, return_value=return_value, side_effect=side_effect
        )
        request.addfinalizer(lambda: mocker.stop(mock_method))
        return mock_method

    return mock_wrapper


@pytest.fixture
def mock_func(mocker, request):
    """
    Mocks function.
    After user, stops mock.
    """

    def mock_wrapper(func_name, return_value=None):
        mock_fn = mocker.patch(func_name, return_value=return_value)
        request.addfinalizer(lambda: mocker.stop(mock_fn))
        return mock_fn

    return mock_wrapper


@pytest.fixture
def game_data():
    return {
        "room_id": "abcd",
        "rounds": 3,
        "current_round": 1,
        "levels_per_round": 4,
        "level": 1,
        "default_level": 1,
        "player_1_id": None,
        "player_2_id": None,
        "p1_rounds_won": 0,
        "p2_rounds_won": 1,
        "status": "init",
        "winner_id": None,
        "map": json.dumps(default_map),
    }


@pytest.fixture
def test_map_data():
    return {
        "name": "test_1",
        "data": default_map,
        "level": 1,
    }


@pytest.fixture
def test_map_init():
    return {
        "name": "test_1",
        "map": json.dumps(default_map),
        "level": 1,
    }


@pytest.fixture
def test_map_init_data():
    return {
        "name": "test_1",
        "data": json.dumps(default_map),
        "level": 1,
    }


@pytest.fixture
def test_map(test_db, test_map_init_data):
    map = Maps(**test_map_init_data)
    test_db.session.add(map)
    test_db.session.commit()
    return map


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
