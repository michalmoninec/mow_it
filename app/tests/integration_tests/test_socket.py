from flask_socketio import SocketIOTestClient


def test_socket(socket_client, test_client):
    event = "request_maps_from_server"

    with test_client.session_transaction() as session:
        session["room_id"] = "some_id"

    socket_client.emit(event)
