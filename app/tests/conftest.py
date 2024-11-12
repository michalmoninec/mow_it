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
def test_db(app_and_client):
    app, _ = app_and_client

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def app_and_client():
    app = create_app(config_class="config.TestConfig")
    app.secret_key = "test_key_noodles"
    with app.test_client() as client:
        yield app, client


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

    def mock_wrapper(func_name):
        mock_fn = mocker.patch(func_name)
        request.addfinalizer(lambda: mocker.stop(mock_fn))
        return mock_fn

    return mock_wrapper
