from flask import url_for

from app.models.game_state_model import GameState


def test_get_create_game(test_client, test_db):
    """
    Tests, that GET method to an endpoint "/multiplayer/create/" works correctly.
    Tests cover:
    - Response status code.
    - Request path is correct.
    """
    endpoint = "/multiplayer/create/"
    resp = test_client.get(endpoint)

    assert resp.status_code == 200
    assert resp.request.path == url_for("multiplayer.multiplayer_create_game")


def test_get_join_room_get_user(test_client, test_db):
    """
    Tests, that GET method to an endpoint "/multiplayer/join/<room_id>/" works correctly.
    Tests cover:
    - Response status code.
    - Request path is correct.
    - Checsks, that room_id is in response html.
    """
    room_id = "test_id"
    endpoint = f"/multiplayer/join/{room_id}/"
    resp = test_client.get(endpoint)
    assert resp.status_code == 200
    assert resp.request.path == url_for(
        "multiplayer.join_room_get_user", room_id=room_id
    )
    assert room_id.encode("utf-8") in resp.data


def test_get_multiplayer_game_play_redirect(test_client, test_db):
    """
    Tests GET method to an endpoint "/multiplayer/play/".
    Tests cover:
    - Response status code.
    - Request path is correct.
    - Checsks, that room_id is
    """
    endpoint = "/multiplayer/play/"
    resp = test_client.get(endpoint)
    assert resp.status_code == 307


def test_get_multiplayer_game_play_valid(test_client, test_db):
    """
    TestsGET method to an endpoint "/multiplayer/play/".
    Tests cover:
    - Response status code.
    - Request path is correct.
    - Checsks, that room_id is
    """
    endpoint = "/multiplayer/play/"
    with test_client.session_transaction() as session:
        session["user_id"] = "test_user_id"
        session["room_id"] = "test_room_id"

    resp = test_client.get(endpoint)
    assert resp.status_code == 200


def test_post_get_user_invalid_payload(test_client, test_db):
    """
    Tests POST method to an endpoint "/multiplayer/create/".
    Empty payload.
    Excpeted response status code 400.
    """
    endpoint = "/multiplayer/create/"
    data = {}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 400


def test_post_get_user_user_none(test_client, test_db, mock_method):
    """
    Tests POST method to an endpoint "/multiplayer/create/".
    Empty payload.
    Excpeted response status code 400.
    """
    endpoint = "/multiplayer/create/"
    data = {"user_id": None}
    mock_method(GameState, "create_multiplayer_game_state")
    mock_method(GameState, "create_user_after_room_join")

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 201
    with test_client.session_transaction() as session:
        assert session["user_id"] != None


def test_post_get_user_user_valid(test_client, test_db, mock_method):
    """
    Tests POST method to an endpoint "/multiplayer/create/".
    Empty payload.
    Excpeted response status code 400.
    """
    endpoint = "/multiplayer/create/"
    data = {"user_id": "test_user_id"}
    mock_method(GameState, "create_multiplayer_game_state")
    mock_method(GameState, "create_user_after_room_join")

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 201
    with test_client.session_transaction() as session:
        assert session["user_id"] == "test_user_id"


def test_post_join_room_set_invalid_room_id(test_client, test_db, mock_method):
    """
    Tests POST method to an endpoint "/multiplayer/join/<room_id>/".
    Provided room ID is invalid.
    Returned room ID should be set to None.
    """
    room_id = "non_existing_room_id"
    endpoint = f"/multiplayer/join/{room_id}/"
    data = {"user_id": "test_user_id"}

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 201
    assert resp.get_json()["room_id"] == None


def test_post_join_room_set_valid_room_full_room(
    test_client, test_db, mock_method, game_state, p1_test, p2_test
):
    """
    Tests POST method to an endpoint "/multiplayer/join/<room_id>/".
    Provided room ID is valid.
    Room with provided ID is full.
    Returned room ID should be set to None.
    """
    room_id = game_state.room_id
    endpoint = f"/multiplayer/join/{room_id}/"
    data = {"user_id": "test_user_id"}
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 201
    assert resp.get_json()["room_id"] == None


def test_post_join_room_set_valid_join(
    test_client, test_db, mock_method, game_state, p1_test, p2_test
):
    """
    Tests POST method to an endpoint "/multiplayer/join/<room_id>/".
    Provided room ID is valid.
    Room with provided ID is full.
    Returned room ID should be set to None.
    """
    room_id = game_state.room_id
    endpoint = f"/multiplayer/join/{room_id}/"
    user_id = "test_user_id"
    data = {"user_id": user_id}
    game_state.add_player(p1_test.user_id)

    resp = test_client.post(endpoint, json=data)
    assert resp.status_code == 201
    assert resp.get_json()["room_id"] == game_state.room_id
    assert resp.get_json()["user_id"] == user_id
