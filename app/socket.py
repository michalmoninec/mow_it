import json

from flask import session
from flask_socketio import emit, join_room
from app.scripts.game import (
    game_state_advance_current_level,
    game_state_advance_ready,
    game_state_status,
    game_state_update,
)
from app.models import GameState, get_map_by_user, get_user_by_id

from app.extensions import db
from app.enums import Status


def configure_socketio(socketio):
    @socketio.on("join_room")
    def handle_join_room() -> None:
        player_id = session["player_id"]
        room = session["room_id"]

        join_room(room)
        print(f"Joined room: {room}")
        game_status = game_state_status(room_id=room)

        emit(
            "response_player_id_and_status",
            {"player_id": session["player_id"], "game_status": game_status},
        )

    @socketio.on("request_maps_from_server")
    def handle_maps_from_server():
        room = session["room_id"]
        emit("response_maps_from_server", to=room)

    @socketio.on("request_initial_maps")
    def get_initial_maps():
        player_id = session["player_id"]
        room = session["room_id"]

        user_state = get_user_by_id(user_id=player_id)

        emit(
            "response_update_data",
            {
                "player_id": player_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
            },
            to=room,
        )

    @socketio.on("request_update_data")
    def handle_update_values(data):
        player_id = session["player_id"]
        room = session["room_id"]
        key = data["key"]

        game_state_update(key=key, user_id=player_id)

        user_state = get_user_by_id(user_id=player_id)

        emit(
            "response_update_data",
            {
                "player_id": player_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
            },
            to=room,
        )

    @socketio.on("request_level_advance_confirmation")
    def handle_level_advance_confirmation():
        player_id = session["player_id"]
        room = session["room_id"]

        emit("response_player_finished_level", {"player_id": player_id}, to=room)

        if game_state_advance_ready(room_id=room):
            emit("response_advance_level_confirmation", to=room)

    @socketio.on("request_level_advance")
    def handle_level_advance():
        player_id = session["player_id"]
        room = session["room_id"]

        game_state_advance_current_level(user_id=player_id)
        user_state = get_user_by_id(user_id=player_id)
        user_state.reset_map()

        emit(
            "response_update_data",
            {
                "player_id": player_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
            },
            to=room,
        )

    @socketio.on("request_game_finished")
    def handle_game_finished():
        emit(
            "response_player_finished_game",
            {"player_id": session["player_id"]},
            to=session["room_id"],
        )

    @socketio.on("disconnect")
    def handle_disconnect():
        player_id = session.get("player_id")

        print(f"Player {player_id} disconnected")
