from flask import session
from flask_socketio import emit, join_room
from .scripts.game import game_update


def configure_socketio(socketio):
    @socketio.on("joined")
    def handle_connect():
        player_id = session["player_id"]
        map = session["map"]
        room = session["room_id"]

        join_room(room)
        print(f"Joined room: {room}")
        emit("retrieve_map", {"map": map, "player_id": player_id})

    @socketio.on("connect")
    def handle_connect():
        print("somebody connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        player_id = session.get("player_id")

        print(f"Player {player_id} disconnected")

    @socketio.on("update_values")
    def update(data):
        player_id = session["player_id"]
        key = data["key"]

        game_update(key, session)
        emit(
            "update_grid",
            {"map": session["map"], "player_id": player_id},
            broadcast=True,
        )
