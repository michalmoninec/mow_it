def test_socket(client, test_client, socket_client):
    event = "request_maps_from_server"

    with test_client.session_transaction() as session:
        session["room_id"] = "1234"
        session["user_id"] = "room_id"
        socketio_test_client = socket_client(session)
        socketio_test_client.emit(event)
