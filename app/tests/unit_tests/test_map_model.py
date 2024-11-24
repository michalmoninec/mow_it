from app.models.map_model import Maps


def test_maps_init(test_map_init_data):
    """
    Tests, that init method works correctly.
    """
    map = Maps(**test_map_init_data)
    for key in test_map_init_data:
        assert map.__getattribute__(key) == test_map_init_data[key]
