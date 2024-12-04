from app.scripts.game import user_get_achieved_levels, create_maps
from app.models.map_model import Maps


def test_user_get_achieved_levels(test_db, mock_method, test_map_data, test_user):
    """Tests, that list of directories containing
    level and map data is returned correctly.
    """
    mock_method(Maps, "get_map_by_level", return_value=test_map_data)

    assert user_get_achieved_levels("non_exist") == None

    test_user.achieved_level = 3
    returned_levels = [
        {"level": level, "data": test_map_data}
        for level in range(1, test_user.achieved_level + 1)
    ]

    assert user_get_achieved_levels(test_user.user_id) == returned_levels


def test_create_maps_not_empty(test_db, test_map_create, mock_method):
    """Tests, that map creation and storing to database works correctly.
    Tests situation where table is not empty.
    Returned value should be False and no creation should be called.
    """
    Maps.create_maps_database(**test_map_create)
    mock_db_creation = mock_method(Maps, "create_maps_database")
    assert create_maps() == False
    assert mock_db_creation.call_count == 0


def test_create_maps_empty(test_db, mock_method):
    """Tests, that map creation and storing to database works correctly.
    For empty Maps table, for every level, map should be created with
    method create_maps_database.
    Returned value should be True and mocked method should be called for every
    level.
    """
    mock_db_creation = mock_method(Maps, "create_maps_database")
    assert create_maps() == True
    assert mock_db_creation.call_count > 0
