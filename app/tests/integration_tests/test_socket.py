import copy
import json

from app.models.game_state_model import GameState


def test_join_room_no_id(socket_client, test_db):
    """
    Tests socketio on event for event name: "join_room".
    Session data is empty.
    Expected received event name is "error".
    Message included inside received event should be concerned about invalid session data.

    """
    event_name = "join_room"
    payload = {}
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) > 0, "No events received from the server."
    assert [event for event in received_events if event["name"] == "error"]
    assert received_events[0]["args"][0]["message"] == "Missing field."


def test_join_room_no_game_state(socket_client, test_db):
    """
    Tests socketio on event for event name: "join_room".
    Session data is set to non-existent values.
    Expected received event name is "error".
    """
    event_name = "join_room"
    payload = {"user_id": "1234", "room_id": "abcd"}

    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) > 0, "No events received from the server."
    assert [event for event in received_events if event["name"] == "error"]
    assert received_events[0]["args"][0]["message"] == "Room not found in databse"


def test_join_room_no_valid_game_state(socket_client, test_db, test_game, p1_test):
    """
    Tests socketio on event for event name: "join_room".
    Session data is valid.
    Expected received event name is "response_user_id_and_status".
    """
    event_name = "join_room"
    payload = {
        "user_id": p1_test.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) > 0, "No events received from the server."
    assert [
        event
        for event in received_events
        if event["name"] == "response_user_id_and_status"
    ]


def test_handle_maps_from_server_invalid_payload(socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is empty.
    Expected received event name is "error".
    """
    event_name = "request_maps_from_server"
    payload = {}
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) > 0
    assert [event for event in received_events if event["name"] == "error"]


def test_handle_maps_from_server_not_joined(socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is valid.
    Expected number of received events is zero, because room is not joined.
    """
    event_name = "request_maps_from_server"
    payload = {
        "user_id": "1234",
        "room_id": "1234",
    }

    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) == 0


def test_handle_maps_from_server_valid(socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is empty.
    Expected number of received events is zero.
    """
    event_name = "request_maps_from_server"
    join_event = "test_join_room"
    payload = {
        "user_id": "1234",
        "room_id": "1234",
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()

    assert len(received_events) > 0
    assert [
        event
        for event in received_events
        if event["name"] == "response_maps_from_server"
    ]


def test_get_inital_maps(socket_client, test_game, test_user):
    """
    Tests socketio on event for event name: "request_initial_maps".
    Expected number of received events is two:
    response_update_data,
    response_round_update.
    """
    event_name = "request_initial_maps"
    join_event = "test_join_room"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    resp_user_data = received_events[0]["args"][0]
    test_user.map = json.loads(test_user.map)
    for key in resp_user_data:
        assert resp_user_data[key] == test_user.__getattribute__(key)

    resp_room_data = received_events[1]["args"][0]
    assert resp_room_data["round"] == test_game.current_round


def test_handle_update_values(socket_client, test_user, test_game):
    """
    Tests socketio on evenet for event name: "request_update_data".
    Excpected is one received event.
    Assumed valid move with ArrowDown, returned map should differs with
    """
    map = copy.deepcopy(json.loads(test_user.map))
    join_event = "test_join_room"
    event_name = "request_update_data"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
        "key": "ArrowDown",
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    resp_user_data = received_events[0]["args"][0]
    assert resp_user_data["map"] != map


def test_handle_level_advance_confirmation_first_player(
    socket_client, test_user, test_game, test_db
):
    """
    Tests socketio on event for event name: request_level_advance_confirmation.
    Test covers situation, where player, that finishes level is first one to do it.
    Game is not ready to advance and player is assigned level bonus.
    """
    join_event = "test_join_room"
    event_name = "request_level_advance_confirmation"
    score = test_user.score
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }
    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_player_finished_level"
    assert received_events[1]["name"] == "response_score_update"
    resp_data = received_events[1]["args"][0]
    assert resp_data["score"] == score + 300


def test_handle_level_advance_confirmation_advance(
    socket_client, test_user, test_game, mock_method
):
    """
    Tests socketio on event for event name: request_level_advance_confirmation.
    Test covers situation, where player, that finishes level is first one to do it.
    Game is ready to advance.
    """
    join_event = "test_join_room"
    event_name = "request_level_advance_confirmation"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }
    mock_method(GameState, "game_state_advance_ready", return_value=True)

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_player_finished_level"
    assert received_events[1]["name"] == "response_advance_level_confirmation"


def test_handle_level_advance(socket_client, test_user, test_game):
    """
    Tests socketio on event for event name: request_level_advance_confirmation.
    Users level should be increased and map set to correspond with map with the same level.
    """
    join_event = "test_join_room"
    event_name = "request_level_advance"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_update_data"


def test_handle_game_finished_not_finished(
    socket_client, test_user, test_game, mock_method
):
    """
    Tests socketio on event for event name: request_game_finished.
    Only one player finished.
    Bonus should be assigned.
    First received event name should be: response_player_finished_game
    """
    join_event = "test_join_room"
    event_name = "request_game_finished"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }
    mock_method(GameState, "both_players_completed_game", return_value=False)

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_player_finished_game"


def test_handle_game_finished_regular_round(
    socket_client, test_user, test_game, mock_method
):
    """
    Tests socketio on event for event name: request_game_finished.
    Both players finished, but it is not final round.
    First received event name should be: response_player_finished_game
    """
    join_event = "test_join_room"
    event_name = "request_game_finished"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }
    mock_method(GameState, "both_players_completed_game", return_value=True)
    mock_method(GameState, "update_round_winner")
    mock_method(GameState, "advance_next_round")
    mock_method(GameState, "final_round", return_value=False)

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_maps_from_server"


def test_handle_game_finished_final_round(
    socket_client, test_user, test_game, mock_method
):
    """
    Tests socketio on event for event name: request_game_finished.
    Both players finished and it is final round.
    First received event name should be: response_player_finished_game
    """
    join_event = "test_join_room"
    event_name = "request_game_finished"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }
    mock_method(GameState, "both_players_completed_game", return_value=True)
    mock_method(GameState, "update_round_winner")
    mock_method(GameState, "update_game_winner")
    mock_method(GameState, "final_round", return_value=True)

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_player_finished_all_rounds"


def test_handle_data_update(socket_client, test_user, test_game):
    """
    Tests socketio on event for event name: request_data_update.
    Received events should be:
    "response_score_update"
    "response_round_update"
    """
    join_event = "test_join_room"
    event_name = "request_data_update"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_score_update"
    assert received_events[1]["name"] == "response_round_update"


def test_handle_game_state_reset(socket_client, test_user, test_game):
    """
    Tests socketio on event for event name: request_game_state_reset.
    Received events should be:
    "response_maps_from_server"
    """
    join_event = "test_join_room"
    event_name = "request_game_state_reset"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_maps_from_server"


def test_handle_disconnect(socket_client, test_user, test_game):
    """
    Tests socketio on event for event name: disconnect.
    Received events should be:
    "response_player_disconnected"
    """
    join_event = "test_join_room"
    event_name = "disconnect"
    payload = {
        "user_id": test_user.user_id,
        "room_id": test_game.room_id,
    }

    socket_client.emit(join_event, payload)
    socket_client.emit(event_name, payload)
    received_events = socket_client.get_received()
    assert received_events[0]["name"] == "response_player_disconnected"
