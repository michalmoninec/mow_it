import json

from app.models.map_model import Maps
from app.scripts.game import create_empty_map


def test_maps_init():
    """
    Tests, that init method behaves correctly.
    """
    test_data = {
        "name": "test_1",
        "start_position": "some_text",
        "level": 1,
        "data": json.dumps(create_empty_map()),
    }

    map = Maps(**test_data)
    for key in test_data:
        assert map.__getattribute__(key) == test_data[key]
