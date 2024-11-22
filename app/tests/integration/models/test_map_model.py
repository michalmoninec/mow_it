import json

from sqlalchemy import delete

from app.models.map_model import Maps


def test_create_maps_database(test_db, test_map_init):
    """
    Tests, that creation and store to db is correct.
    """
    Maps.create_maps_database(**test_map_init)

    map = test_db.session.query(Maps).filter_by(name="test_1").first()
    assert map is not None
    assert map.name == test_map_init["name"]
    assert map.level == test_map_init["level"]
    assert map.data == json.dumps(test_map_init["map"])


def test_get_max_level_of_maps(test_db, test_map_init):
    """
    Tests, that maximal level of maps is correct.
    """
    assert Maps.get_max_level_of_maps() is None

    for level in range(1, 10):
        test_map_init["level"] = level
        Maps.create_maps_database(**test_map_init)
        assert Maps.get_max_level_of_maps() == level


def test_get_map_by_level(test_db, test_map_init):
    """
    Tests, that getting map by level is correct.
    """
    assert Maps.get_map_by_level(test_map_init["level"]) == None

    Maps.create_maps_database(**test_map_init)

    map = Maps.get_map_by_level(test_map_init["level"])
    assert map is not None
    assert map == json.dumps(test_map_init["map"])


def test_is_map_table_empty(test_db, test_map_init):
    """
    Tests, that evaluation of an empty table is correct.
    """
    assert Maps.is_map_table_empty() == True

    Maps.create_maps_database(**test_map_init)

    assert Maps.is_map_table_empty() == False

    test_db.session.execute(delete(Maps))
    test_db.session.commit()

    assert Maps.is_map_table_empty() == True