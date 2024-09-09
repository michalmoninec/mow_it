import json

from flask import session
from flask_socketio import emit, join_room
from app.scripts.game import (
    game_state_advance_current_level,
    user_state_update,
)
from app.models import (
    GameState,
    game_state_advance_ready,
    get_game_state_status,
    get_game_state_by_room,
    get_game_state_max_level_by_room,
    get_user_by_id,
)

from app.extensions import db
from app.enums import Status


def configure_socketio(socketio):
    @socketio.on("join_room")
    def handle_join_room() -> None:
        room = session["room_id"]

        # TODO check if room is available and user is alocated to this room
        join_room(room)
        print(f"Joined room: {room}")
        game_status = get_game_state_status(room_id=room)

        emit(
            "response_user_id_and_status",
            {"user_id": session["user_id"], "game_status": game_status},
        )

    @socketio.on("request_maps_from_server")
    def handle_maps_from_server():
        room = session["room_id"]
        emit("response_maps_from_server", to=room)

    @socketio.on("request_initial_maps")
    def get_initial_maps():
        user_id = session["user_id"]
        room = session["room_id"]

        user_state = get_user_by_id(user_id)

        emit(
            "response_update_data",
            {
                "user_id": user_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
                "rounds_won": user_state.rounds_won,
            },
            to=room,
        )

        emit(
            "response_round_update",
            {"round": get_game_state_by_room(session["room_id"]).current_round},
            to=session["room_id"],
        )

    @socketio.on("request_update_data")
    def handle_update_values(data):
        user_id = session["user_id"]
        room = session["room_id"]
        key = data["key"]
        max_level = get_game_state_max_level_by_room(room)

        user_state_update(key, user_id, max_level)

        user_state = get_user_by_id(user_id=user_id)
        print(f"User completed level: {user_state.level_completed}")

        emit(
            "response_update_data",
            {
                "user_id": user_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
                "rounds_won": user_state.rounds_won,
            },
            to=room,
        )

    @socketio.on("request_level_advance_confirmation")
    def handle_level_advance_confirmation():
        user_id = session["user_id"]
        room = session["room_id"]

        user_state = get_user_by_id(user_id)

        emit("response_player_finished_level", {"user_id": user_id}, to=room)

        if game_state_advance_ready(room_id=room):
            emit("response_advance_level_confirmation", to=room)
        else:
            user_state.set_score(300)
            emit(
                "response_score_update",
                {
                    "user_id": user_id,
                    "score": user_state.score,
                    "rounds_won": user_state.rounds_won,
                },
                to=session["room_id"],
            )

    @socketio.on("request_level_advance")
    def handle_level_advance():
        user_id = session["user_id"]
        room = session["room_id"]
        max_level = get_game_state_max_level_by_room(room)
        print(f"Max level is: {max_level}")
        game_state_advance_current_level(user_id, max_level)
        user_state = get_user_by_id(user_id=user_id)
        user_state.reset_map()

        emit(
            "response_update_data",
            {
                "user_id": user_id,
                "map": json.loads(user_state.map),
                "level": user_state.level,
                "score": user_state.score,
                "name": user_state.name,
                "level_completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
                "rounds_won": user_state.rounds_won,
            },
            to=room,
        )

    @socketio.on("request_game_finished")
    def handle_game_finished():
        game_state = get_game_state_by_room(session["room_id"])
        user_state = get_user_by_id(session["user_id"])

        if game_state.both_players_completed_game():
            game_state.update_round_winner()

            if game_state.final_round():
                game_state.set_status(Status.FINISHED.value)
                game_state.update_game_winner()
                emit(
                    "response_player_finished_all_rounds",
                    {"user_id": session["user_id"], "winner_id": game_state.winner_id},
                    to=session["room_id"],
                )
            else:

                game_state.advance_next_round()

                emit("response_maps_from_server", to=session["room_id"])
        else:
            emit("response_player_finished_game", {"user_id": session["user_id"]})
            user_state.set_score(300)

        emit(
            "response_score_update",
            {
                "user_id": user_state.user_id,
                "score": user_state.score,
                "rounds_won": user_state.rounds_won,
            },
            to=session["room_id"],
        )
        emit(
            "response_round_update",
            {"round": game_state.current_round},
            to=session["room_id"],
        )

    @socketio.on("request_game_state_reset")
    def handle_game_state_reset():
        game_state = get_game_state_by_room(session["room_id"])
        game_state.reset_game_state()
        emit("response_maps_from_server", to=session["room_id"])

    @socketio.on("disconnect")
    def handle_disconnect():
        user_id = session["user_id"]

        print(f"Player {user_id} disconnected")
