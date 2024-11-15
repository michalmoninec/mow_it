from flask import session, url_for

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


def test_post_single_player_level_data_user_not_included(test_client, test_db):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    empty json.
    Excpected response status code: 400.
    """

    endpoint = "/single_player/level_data/"
    data = {}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400


def test_post_single_player_level_data_user_doesnt_exist(test_client, test_db):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that is stored in session, but is not present in database.
    Excpected response status code: 404.
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": "non_existing"}

    with test_client.session_transaction() as session:
        session["user_id"] = data["user_id"]

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 404


def test_post_single_player_level_data_user_none(test_client, test_db):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that is None, is stored in session.
    Excpected response status code: 200.
    New user creation with uuid user ID should have happend.
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": None}

    with test_client.session_transaction() as session:
        session["user_id"] = data["user_id"]

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] != data["user_id"]


def test_post_single_player_level_data_user_not_in_session(test_client, test_db):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that is not inside session and database.
    Excpected response status code: 200.
    New user created with provided user ID by POST method.
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": "not_in_session"}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == data["user_id"]


def test_post_single_player_level_data_user_exists_not_in_session(
    test_client, test_db, test_user_state, mock_method
):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that has existing UserState in database.
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
    with test_client.session_transaction() as session:
        assert session["user_id"] == test_user_state.user_id
    assert mock_user_creation.call_count == 0


def test_post_single_player_level_data_user_exists_and_in_session(
    test_client, test_db, test_user_state, mock_method
):
    """
    Tests POST request to endpoint '/single_player/level_data/' with
    user's ID that has existing UserState in database and ID is stored in session.
    Excpected response status code: 200.
    Response users ID must be same as provided with POST method.
    UserState was already existing before post, so it shouldnt be called after.
    """

    endpoint = "/single_player/level_data/"
    data = {"user_id": test_user_state.user_id}
    mock_user_creation = mock_method(UserState, "create_user_state")
    with test_client.session_transaction() as session:
        session["user_id"] = data["user_id"]

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == test_user_state.user_id
    with test_client.session_transaction() as session:
        assert session["user_id"] == test_user_state.user_id
    assert mock_user_creation.call_count == 0


def test_set_selected_level_empty_payload(test_client, test_db, test_user_state):
    """
    Tests POST request to endpoint "/single_player/selected_level/".
    Request, that doesnt include desired_level.
    Excpected response status code 400.
    """

    endpoint = "/single_player/selected_level/"
    data = {}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400
    assert b"Desired level not provided." in resp.data


def test_set_selected_level_id_not_in_session(test_client, test_db, test_user_state):
    """
    Tests POST request to endpoint "/single_player/selected_level/".
    User's ID is not in session.
    Excpected response status code 400.
    """

    endpoint = "/single_player/selected_level/"
    data = {"selected_level": 5}
    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400
    assert b"User ID not in session." in resp.data


def test_set_selected_level_valid_set(test_client, test_db, test_user_state):
    """
    Tests POST request to endpoint "/single_player/selected_level/".
    Selected level and user ID are correct.
    Selected level is less or equal to achieved level.
    Excpected response status code 200, valid_level_set = True.
    """

    endpoint = "/single_player/selected_level/"
    with test_client.session_transaction() as session:
        session["user_id"] = test_user_state.user_id
    data = {"selected_level": test_user_state.achieved_level}
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
    data = {"selected_level": test_user_state.achieved_level + 1}
    with test_client.session_transaction() as session:
        session["user_id"] = test_user_state.user_id
    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["valid_level_set"] == False


def test_init_map_invalid_user(test_client, test_db):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is provided and is in session.
    No UserState exists with this ID.
    Excpected response status code 400.
    """

    endpoint = "/single_player/retrieve_map/"
    data = {"user_id": "non_existing"}
    with test_client.session_transaction() as session:
        session["user_id"] = data["user_id"]

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400


def test_init_map_user_exists_and_in_session(
    test_client, test_db, test_user_state, test_map
):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is provided and is in session.
    UserState exists with this ID.
    Excpected response status code 200.
    """

    endpoint = "/single_player/retrieve_map/"
    data = {"user_id": test_user_state.user_id}
    with test_client.session_transaction() as session:
        session["user_id"] = test_user_state.user_id

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == test_user_state.user_id


def test_init_map_user_is_none_not_in_session(
    test_client, test_db, test_user_state, test_map
):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is not provided and is in session.
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


def test_init_map_user_exists_and_not_in_session(
    test_client, test_db, test_user_state, test_map
):
    """
    Tests POST request to endpoint "/single_player/retrieve_map/".
    User's ID is not provided and is in session.
    UserState does not exist with this ID.
    Excpected response status code 200.
    New UserState with uuid user's ID is created.
    """

    endpoint = "/single_player/retrieve_map/"
    data = {"user_id": test_user_state.user_id}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data["user_id"] == test_user_state.user_id
    with test_client.session_transaction() as session:
        assert session["user_id"] == test_user_state.user_id


def test_move_handle_invalid_key(test_client, test_db, test_user_state, test_map):
    """
    Tests POST request to endpoint "/single_player/move/".
    No key in json request.
    """

    endpoint = "/single_player/move/"
    data = {}

    resp = test_client.post(endpoint, json=data)

    assert resp.status_code == 400
    assert b"Key was not provided." in resp.data


def test_move_handle_no_id_in_session(test_client, test_db, test_user_state, test_map):
    """
    Tests POST request to endpoint "/single_player/move/".
    Key is provided.
    Provided ID does not correspond with existing UserState.
    """

    endpoint = "/single_player/move/"
    data = {"key": "ArrowUp"}

    resp = test_client.post(endpoint, json=data)

    assert resp.status_code == 400
    assert b"No User ID in session." in resp.data


def test_move_handle_user_does_not_exist(test_client, test_db):
    """
    Tests POST request to endpoint "/single_player/move/".
    Key is provided.
    User ID is in session.
    UserState with provided ID does not exist.
    """

    endpoint = "/single_player/move/"
    data = {"key": "ArrowUp"}
    with test_client.session_transaction() as session:
        session["user_id"] = "non_existing"

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400
    assert b"Invalid user." in resp.data


def test_move_handle_valid(test_client, test_db, test_user_state, test_map, mock_func):
    """
    Tests POST request to endpoint "/single_player/move/".
    Key is provided.
    User ID is in session.
    UserState with provided ID exists.
    """
    return_coords = (1, 1)
    mock_func("app.scripts.game.get_position_from_map", return_value=return_coords)
    mock_func("app.scripts.game.validate_move", return_value=return_coords)

    endpoint = "/single_player/move/"
    data = {"key": "ArrowUp"}
    with test_client.session_transaction() as session:
        session["user_id"] = test_user_state.user_id

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 200


def test_advance_curr_level_invalid_session(test_client, test_db):
    """
    Tests POST request to endpoint "/single_player/advance_current_level/".
    User ID is not stored in session.
    """

    endpoint = "/single_player/advance_current_level/"

    resp = test_client.post(endpoint, json={})
    assert resp.status_code == 400


def test_advance_curr_level_invalid_advance(test_client, test_db, mock_method):
    """
    Tests POST request to endpoint "/single_player/advance_current_level/".
    User ID is not stored in session.
    """

    endpoint = "/single_player/advance_current_level/"
    with test_client.session_transaction() as session:
        session["user_id"] = "some_id"

    mock_method(UserState, "advance_user_state_current_level", return_value=False)

    resp = test_client.post(endpoint, json={})
    assert resp.status_code == 200
    assert resp.get_json()["valid_advance"] == False


def test_advance_curr_level_valid_advance(test_client, test_db, mock_method):
    """
    Tests POST request to endpoint "/single_player/advance_current_level/".
    User ID is not stored in session.
    """

    endpoint = "/single_player/advance_current_level/"
    with test_client.session_transaction() as session:
        session["user_id"] = "some_id"

    mock_method(UserState, "advance_user_state_current_level", return_value=True)

    resp = test_client.post(endpoint, json={})
    assert resp.status_code == 200
    assert resp.get_json()["valid_advance"] == True
