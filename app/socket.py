import json

from flask import jsonify, session
from flask_socketio import emit, join_room
from app.scripts.game import game_state_advance_current_level, game_state_update
from app.models import GameState, get_map_by_user

from app.extensions import db


def configure_socketio(socketio):
    @socketio.on("joined")
    def handle_connect():
        player_id = session["player_id"]
        room = session["room_id"]

        join_room(room)
        print(f"Joined room: {room}")

        map = json.loads(get_map_by_user(user_id=player_id))

        emit(
            "retrieve_player_id",
            {"player_id": session["player_id"]},
        )

        emit(
            "update_grid",
            {"map": map, "player_id": player_id},
            broadcast=True,
        )

    @socketio.on("disconnect")
    def handle_disconnect():
        player_id = session.get("player_id")

        print(f"Player {player_id} disconnected")

    @socketio.on("update_values")
    def update(data):
        player_id = session["player_id"]
        key = data["key"]
        print(key)

        updated_game_state = game_state_update(key=key, user_id=player_id)
        map = updated_game_state["map"]
        level_finished = updated_game_state["completed"]

        emit(
            "update_grid",
            {"map": map, "player_id": player_id},
            broadcast=True,
        )

        if level_finished:
            game_state_advance_current_level(user_id=player_id)
            map = json.loads(get_map_by_user(user_id=player_id))
            emit(
                "update_grid",
                {"map": map, "player_id": player_id},
                broadcast=True,
            )
