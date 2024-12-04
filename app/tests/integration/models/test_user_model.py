import json, pytest

from sqlalchemy.exc import ProgrammingError

from app.models.user_model import UserState, LEVEL_BONUS
from app.models.map_model import Maps
from app.scripts.game import create_empty_map


def reset_mocks(*mocks) -> None:
    """Reset all provided mocks."""
    for mock in mocks:
        mock.reset_mock()


def object_is_same_in_db(state: UserState) -> bool:
    """Checks if state object is the same as an object
    from database with matching user_id.
    """
    return UserState.query.filter_by(user_id=state.user_id).first() == state


def test_set_level(test_db, test_user, test_user_data):
    """Tests, that setting user's level is correct.
    Checks that UserState object and match from db.query are correctly set.
    """
    assert test_user.level == test_user_data["level"]

    level = 99

    with pytest.raises(ProgrammingError):
        test_user.set_level({"not": "str compatitble"})
    test_db.session.rollback()

    test_user.set_level(level)

    assert test_user.level == level

    assert object_is_same_in_db(test_user)


def test_set_map(test_db, test_user, test_user_data):
    """Tests, that setting user's map is correct.
    Checks that UserState object and match from db.query are correctly set.
    """
    assert test_user.map == test_user_data["map"]

    map = json.dumps(create_empty_map())

    with pytest.raises(ProgrammingError):
        test_user.set_map({"not": "str compatible"})
    test_db.session.rollback()

    test_user.set_map(map)

    assert test_user.map == map
    assert object_is_same_in_db(test_user)


def test_increase_level(test_db, test_user, test_user_data):
    """Tests, that level increase is working correctly.
    Tests. that level is increased at UserState object and also in db query.
    """
    max_level = 2
    assert test_user.level == test_user_data["level"]
    assert test_user.achieved_level == test_user_data["achieved_level"]

    test_user.increase_level(max_level)
    assert test_user.level == test_user_data["level"] + 1
    assert test_user.achieved_level == test_user_data["achieved_level"] + 1
    assert object_is_same_in_db(test_user)

    test_user.increase_level(max_level)
    assert test_user.level == max_level
    assert test_user.achieved_level == max_level
    assert object_is_same_in_db(test_user)


def test_set_name(test_db, test_user, test_user_data):
    """Tests, that setting user's name is correct.
    Checks that UserState object and match from db.query are correctly set.
    """
    assert test_user.name == test_user_data["name"]

    with pytest.raises(ProgrammingError):
        test_user.set_name({"not": "valid"})
    test_db.session.rollback()

    name = "jane done"
    test_user.set_name(name)
    assert test_user.name == name
    assert object_is_same_in_db(test_user)


def test_add_score(test_db, test_user, test_user_data):
    """Tests, that score addition is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    assert test_user.score == test_user_data["score"]

    score_diff = 100
    test_user.add_score(score_diff)
    assert test_user.score == test_user_data["score"] + score_diff
    assert object_is_same_in_db(test_user)


def test_reset_score(test_db, test_user_data, test_user):
    """Tests, that reset of user's score is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    test_user.score == 1000
    test_user.reset_score()

    assert test_user.score == 0
    assert object_is_same_in_db(test_user)


def test_set_level_completed(test_db, test_user, test_user_data):
    """Tests, that setting of level completion is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    assert test_user.level_completed == False
    test_user.set_level_completed(True)
    assert test_user.level_completed == True
    assert object_is_same_in_db(test_user)
    test_user.set_level_completed(False)
    assert test_user.level_completed == False
    assert object_is_same_in_db(test_user)


def test_set_game_completed(test_db, test_user, test_user_data):
    """Tests, that setting of game completion is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    assert test_user.game_completed == False
    test_user.set_game_completed(True)
    assert test_user.game_completed == True
    assert object_is_same_in_db(test_user)
    test_user.set_game_completed(False)
    assert test_user.game_completed == False
    assert object_is_same_in_db(test_user)


def test_reset_map(test_db, test_user, mock_method):
    """Tests, that map reset is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    return_map = json.dumps({"test": "test_return_map"})
    mock_method(Maps, "get_map_by_level", return_value=return_map)

    test_user.reset_map()

    assert test_user.map == return_map
    assert object_is_same_in_db(test_user)


def test_set_desired_level(test_db, test_user):
    """Tests, that setting desired level is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    des_level = test_user.achieved_level + 1

    assert test_user.set_desired_level(des_level) == False
    assert test_user.level != des_level
    assert object_is_same_in_db(test_user)

    test_user.achieved_level = des_level
    assert test_user.set_desired_level(des_level) == True
    assert test_user.level == des_level
    assert object_is_same_in_db(test_user)


def test_set_default_state_by_level(test_db, test_user, mock_method):
    """Tests, that map reset is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    return_map = json.dumps({"test": "test_return_map"})
    mock_method(Maps, "get_map_by_level", return_value=return_map)

    test_user.score = 1000
    test_user.level_completed = True
    test_user.game_completed = True
    assert test_user.map != return_map

    test_user.set_default_state_by_level()
    assert test_user.score == 0
    assert test_user.map == return_map
    assert test_user.level_completed == False
    assert test_user.game_completed == False
    assert object_is_same_in_db(test_user)


def test_assign_level_bonus(test_db, test_user):
    """Tests, that bonus was assigned to score.
    Checks, that UserState object and match from db.query are correctly set.
    """
    init_value = 1000
    test_user.score = init_value

    test_user.assign_level_bonus()
    assert test_user.score == init_value + LEVEL_BONUS
    assert object_is_same_in_db(test_user)


def test_advance_user_state_current_level(test_db, test_user, mock_method):
    """Tests, that user state advance is working correctly.
    Checks, that UserState object and match from db.query are correctly set.
    """
    return_level = 3
    return_map = json.dumps({"test": "test_return_map"})
    mock_method(Maps, "get_max_level_of_maps", return_value=return_level)
    mock_method(UserState, "get_user_by_id", return_value=test_user)
    mock_method(Maps, "get_map_by_level", return_value=return_map)
    mock_increase = mock_method(UserState, "increase_level")
    mock_reset_map = mock_method(UserState, "reset_map")

    test_user.level_completed = True
    assert (
        UserState.advance_user_state_current_level("does_not_matter_fnc_mocked") == True
    )
    mock_increase.assert_called_with(return_level)
    assert mock_reset_map.call_count == 1
    reset_mocks(mock_reset_map, mock_increase)

    level = 55
    assert (
        UserState.advance_user_state_current_level("does_not_matter_fnc_mocked", level)
        == True
    )
    mock_increase.assert_called_with(level)
    assert mock_reset_map.call_count == 1
    assert mock_increase.call_count == 1
    reset_mocks(mock_reset_map, mock_increase)

    test_user.level_completed = False
    assert (
        UserState.advance_user_state_current_level("does_not_matter_fnc_mocked")
        == False
    )
    assert mock_reset_map.call_count == 0
    assert mock_increase.call_count == 0

    mock_method(UserState, "get_user_by_id", return_value=None)
    assert (
        UserState.advance_user_state_current_level("does_not_matter_fnc_mocked")
        == False
    )
    assert mock_reset_map.call_count == 0
    assert mock_increase.call_count == 0


def test_get_user_by_id(test_db, test_user):
    """Tests, that getting user by id from database works correctly."""
    assert UserState.get_user_by_id(test_user.user_id) == test_user
    assert UserState.get_user_by_id("non_existing_id") == None


def test_create_user_state(
    test_db,
    test_creation_data,
    mock_method,
    test_map_data,
):
    """Tests, that user state creation works correctly."""
    user_id = test_creation_data["user_id"]
    level = test_creation_data["level"]
    mock_method(Maps, "get_map_by_level", return_value=json.dumps(test_map_data))

    UserState.create_user_state(user_id, level=level)

    created_state = UserState.query.filter_by(user_id=user_id).first()
    for key in test_creation_data:
        assert created_state.__getattribute__(key) == test_creation_data[key]
