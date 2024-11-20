import json


def test_join_room_no_id(test_client, socket_client, test_db):
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


def test_join_room_no_game_state(test_client, socket_client, test_db):
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


def test_join_room_no_valid_game_state(
    test_client, socket_client, test_db, test_game, p1_test
):
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


def test_handle_maps_from_server_invalid_payload(test_client, socket_client):
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


def test_handle_maps_from_server_not_joined(test_client, socket_client):
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


def test_handle_maps_from_server_valid(test_client, socket_client):
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


def test_get_inital_maps(test_client, socket_client, test_game, test_user):
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
