def test_join_room_no_id(test_client, socket_client, test_db):
    """
    Tests socketio on event for event name: "join_room".
    Session data is empty.
    Expected received event name is "error".
    Message included inside received event should be concerned about invalid session data.

    """
    event_name = "join_room"

    with test_client.session_transaction() as session:
        socketio_test_client = socket_client(session)

        socketio_test_client.emit(event_name)

        received_events = socketio_test_client.get_received()

        assert len(received_events) > 0, "No events received from the server."
        assert [event for event in received_events if event["name"] == "error"]
        assert (
            received_events[0]["args"][0]["message"] == "No room or user ID in session."
        )


def test_join_room_no_game_state(test_client, socket_client, test_db):
    """
    Tests socketio on event for event name: "join_room".
    Session data is set to non-existent values.
    Expected received event name is "error".
    """
    event_name = "join_room"

    with test_client.session_transaction() as session:
        session["room_id"] = "non_exist"
        session["user_id"] = "non_exist"
        socketio_test_client = socket_client(session)

        socketio_test_client.emit(event_name)
        received_events = socketio_test_client.get_received()

        assert len(received_events) > 0, "No events received from the server."
        assert [event for event in received_events if event["name"] == "error"]
        assert received_events[0]["args"][0]["message"] == "Invalid GameState."


def test_join_room_no_valid_game_state(
    test_client, socket_client, test_db, game_state, p1_test
):
    """
    Tests socketio on event for event name: "join_room".
    Session data is valid.
    Expected received event name is "response_user_id_and_status".
    """
    event_name = "join_room"

    with test_client.session_transaction() as session:
        session["room_id"] = game_state.room_id
        session["user_id"] = p1_test.user_id
        socketio_test_client = socket_client(session)

        socketio_test_client.emit(event_name)

        received_events = socketio_test_client.get_received()

        assert len(received_events) > 0, "No events received from the server."
        assert [
            event
            for event in received_events
            if event["name"] == "response_user_id_and_status"
        ]


def test_handle_maps_from_server_invalid_session_data(test_client, socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is empty.
    Expected received event name is "error".
    """
    event_name = "request_maps_from_server"
    socketio_test_client = socket_client()
    socketio_test_client.emit(event_name)
    received_events = socketio_test_client.get_received()

    assert len(received_events) > 0
    assert [event for event in received_events if event["name"] == "error"]


def test_handle_maps_from_server_not_joined(test_client, socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is empty.
    Expected received event name is "error".
    """
    event_name = "request_maps_from_server"
    with test_client.session_transaction() as session:

        socketio_test_client = socket_client()
        socketio_test_client.emit(event_name)
        received_events = socketio_test_client.get_received()

        assert len(received_events) > 0
        assert [event for event in received_events if event["name"] == "error"]


def test_handle_maps_from_server_valid(test_client, socket_client):
    """
    Tests socketio on event for event name: "request_maps_from_server".
    Session data is empty.
    Expected number of received events is zero.
    """
    event_name = "request_maps_from_server"
    join_event = "test_join_room"
    with test_client.session_transaction() as session:
        session["room_id"] = "room_id"

        socketio_test_client = socket_client(session)
        socketio_test_client.emit(join_event, {"room_id": "room_id"})
        socketio_test_client.emit(event_name)
        received_events = socketio_test_client.get_received()

        assert len(received_events) > 0
        assert [
            event
            for event in received_events
            if event["name"] == "response_maps_from_server"
        ]


def test_get_inital_maps_invalid_session_data(test_client, socket_client):
    """
    Tests socketio on event for event name: "request_initial_maps".
    Session data is empty.
    Expected number of received events is zero.
    """
    pass
