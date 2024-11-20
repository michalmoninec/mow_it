from flask import url_for

from app.models.user_model import UserState


def test_get_single_player_level_selection(test_client):
    """
    Tests, that endpoint '/single_player/level_selection/' works correctly.
    """

    endpoint = "/single_player/level_selection/"

    resp = test_client.get(endpoint)
    assert resp.status_code == 200
    assert resp.request.path == url_for("singleplayer.single_player_level_selection")


def test_get_single_player_prepare(test_client):
    """
    Tests, that endpoint '/single_player/' works correctly.
    """

    endpoint = "/single_player/"

    resp = test_client.get(endpoint)
    assert resp.status_code == 200
    assert resp.request.path == url_for("singleplayer.single_player_prepare")


def test_post_single_player_level_data_user_exists(
    test_client, test_db, test_user_state, mock_method
):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that has existing UserState in database and ID is in payload.
    Excpected response status code: 200.
    Response users ID must be same as provided with POST method.
    UserState was already existing before post, so it shouldnt be called after.
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": test_user_state.user_id}
    mock_user_creation = mock_method(UserState, "create_user_state")

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == test_user_state.user_id
    assert mock_user_creation.call_count == 0


def test_post_single_player_level_data_user_creation(
    test_client, test_db, test_user_state, mock_method
):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that has existing UserState in database and ID is in payload.
    Excpected response status code: 200.
    Response users ID must be same as provided with POST method.
    UserState was created
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": None}
    mock_user_creation = mock_method(UserState, "create_user_state")

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] != None
    assert mock_user_creation.call_count == 1


def test_set_selected_level_valid_set(test_client, test_db, test_user_state):
    """
    Tests POST request to endpoint "/single_player/selected_level/".
    Selected level and user ID are correct.
    Selected level is less or equal to achieved level.
    Excpected response status code 200, valid_level_set = True.
    """

    endpoint = "/single_player/selected_level/"
    data = {
        "selected_level": test_user_state.achieved_level,
        "user_id": test_user_state.user_id,
    }
    resp = test_client.post(endpoint, json=data)

    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["valid_level_set"] == True


def test_set_selected_level_invalid_set(test_client, test_db, test_user_state):
    """
    Tests POST request to endpoint "/single_player/selected_level/".
    Selected level and user ID are correct.
    Selected level is greater than achieved level.
    Excpected response status code 200, valid_level_set = False.
    """

    endpoint = "/single_player/selected_level/"
    data = {
        "selected_level": test_user_state.achieved_level + 1,
        "user_id": test_user_state.user_id,
    }

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["valid_level_set"] == False


def test_init_map_valid(test_client, test_db, test_user_state, test_map):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is provided and is in payload.
    UserState exists with this ID.
    Excpected response status code 200.
    """

    endpoint = "/single_player/retrieve_map/"
    data = {"user_id": test_user_state.user_id}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == test_user_state.user_id


def test_init_map_user_is_none_not_in_payload(
    test_client, test_db, test_user_state, test_map
):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is not provided and is in payload.
    UserState does not exist with this ID.
    Excpected response status code 200.
    New UserState with uuid user's ID is created.
    """

    endpoint = "/single_player/retrieve_map/"
    data = {"user_id": None}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] != None


def test_move_handle_valid(test_client, test_db, test_user_state, test_map, mock_func):
    """
    Tests POST request to endpoint "/single_player/move/".
    Key is provided.
    User ID is in payload.
    UserState with provided ID exists.
    """
    return_coords = (1, 1)
    mock_func("app.scripts.game.get_position_from_map", return_value=return_coords)
    mock_func("app.scripts.game.validate_move", return_value=return_coords)

    endpoint = "/single_player/move/"
    data = {"key": "ArrowUp", "user_id": test_user_state.user_id}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200


def test_advance_curr_level_invalid_advance(
    test_client, test_db, mock_method, test_user_state
):
    """
    Tests POST request to endpoint "/single_player/advance_current_level/".
    User ID is not stored in payload.
    """

    endpoint = "/single_player/advance_current_level/"
    payload = {"user_id": test_user_state.user_id}
    mock_method(UserState, "advance_user_state_current_level", return_value=False)

    resp = test_client.post(endpoint, json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["valid_advance"] == False


def test_advance_curr_level_valid_advance(
    test_client, test_db, mock_method, test_user_state
):
    """
    Tests POST request to endpoint "/single_player/advance_current_level/".
    User ID is not stored in payload.
    """

    endpoint = "/single_player/advance_current_level/"
    payload = {"user_id": test_user_state.user_id}
    mock_method(UserState, "advance_user_state_current_level", return_value=True)

    resp = test_client.post(endpoint, json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["valid_advance"] == True
