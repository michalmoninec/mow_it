import json

from sqlalchemy import delete

from app.models.map_model import Maps


def test_create_maps_database(test_db):
    """
    Tests, that creation and store to db is correct.
    """
    test_data = {
        "name": "test_1",
        "map": {"test_key": "test_value"},
        "level": 1,
    }

    Maps.create_maps_database(**test_data)

    map = test_db.session.query(Maps).filter_by(name="test_1").first()
    assert map is not None
    assert map.name == test_data["name"]
    assert map.level == test_data["level"]
    assert map.data == json.dumps(test_data["map"])


def test_get_max_level_of_maps(test_db):
    """
    Tests, that maximal level of maps is correct.
    """
    assert Maps.get_max_level_of_maps() is None

    for level in range(1, 10):
        test_data = {
            "name": "test_1",
            "map": {"test_key": "test_value"},
            "level": level,
        }
        Maps.create_maps_database(**test_data)
        assert Maps.get_max_level_of_maps() == level


def test_get_map_by_level(test_db):
    """
    Tests, that getting map by level is correct.
    """
    test_data = {
        "name": "test_1",
        "map": {"test_key": "test_value"},
        "level": 1,
    }
    assert Maps.get_map_by_level(test_data["level"]) == None

    Maps.create_maps_database(**test_data)

    map = Maps.get_map_by_level(test_data["level"])
    assert map is not None
    assert map == json.dumps(test_data["map"])


def test_is_map_table_empty(test_db):
    """
    Tests, that evaluation of an empty table is correct.
    """
    assert Maps.is_map_table_empty() == True

    test_data = {
        "name": "test_1",
        "map": {"test_key": "test_value"},
        "level": 1,
    }
    Maps.create_maps_database(**test_data)

    assert Maps.is_map_table_empty() == False

    test_db.session.execute(delete(Maps))
    test_db.session.commit()

    assert Maps.is_map_table_empty() == True
