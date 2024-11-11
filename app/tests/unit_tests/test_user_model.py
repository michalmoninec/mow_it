import json


from app.models.user_model import UserState
from app.scripts.game import create_empty_map


def test_user_state_init():
    """
    Tests, that init method behaves correctly."""
    test_data = {
        "user_id": "test_user_id",
        "level": 99,
        "achieved_level": 999,
        "score": 100,
        "rounds_won": 0,
        "name": "test_name",
        "game_completed": False,
        "level_completed": False,
        "map": json.dumps(create_empty_map()),
    }

    user_state = UserState(**test_data)

    for key in test_data:
        assert user_state.__getattribute__(key) == test_data[key]
