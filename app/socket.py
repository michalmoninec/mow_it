import json

from flask import session
from flask_socketio import emit, join_room, leave_room
from app.scripts.game import (
    user_state_update,
)

from app.models.game_state_model import UserState, GameState
from app.enums import Status


def configure_socketio(socketio, session=session):
    @socketio.on("join_room")
    def handle_join_room(data) -> None:
        room_id = data.get("room_id")
        user_id = data.get("user_id")
        print(room_id, user_id)
        if room_id and user_id:
            join_room(room_id)
            game_state = GameState.get_game_state_by_room(room_id)
            if game_state:
                if (
                    game_state.user_not_in_room(user_id)
                    and game_state.room_is_available()
                ):
                    game_state.add_player(user_id)

                game_state.update_status()
                game_status = game_state.status

                emit(
                    "response_user_id_and_status",
                    {
                        "user_id": user_id,
                        "game_status": game_status,
                        "room_id": room_id,
                    },
                )
            else:
                emit("error", {"message": "Invalid GameState."})
        else:
            emit("error", {"message": "No room or user ID in session."})

    @socketio.on("request_maps_from_server")
    def handle_maps_from_server(data) -> None:
        room = data.get("room_id")
        if room:
            emit("response_maps_from_server", to=room)
        else:
            emit("error", {"message": "No room ID in session."})

    @socketio.on("request_initial_maps")
    def get_initial_maps(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            user_state = UserState.get_user_by_id(user_id)
            if user_state:
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
                    to=room_id,
                )
            else:
                emit("error", {"message": "Invalid UserState."})

            game_state = GameState.get_game_state_by_room(room_id)
            if game_state:
                emit(
                    "response_round_update",
                    {"round": game_state.current_round},
                    to=room_id,
                )
            else:
                emit("error", {"message": "Invalid GameState."})
        else:
            emit("error", {"message": "No room or user ID in session."})

    @socketio.on("request_update_data")
    def handle_update_values(data: dict) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        key = data.get("key")

        if user_id and room_id:
            max_level = GameState.get_game_state_max_level_by_room(room_id)

            user_state_update(key, user_id, max_level)

            user_state = UserState.get_user_by_id(user_id=user_id)
            if user_state:
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
                        "key": key,
                    },
                    to=room_id,
                )
            else:
                emit("error", {"message": "Invalid UserState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("request_level_advance_confirmation")
    def handle_level_advance_confirmation(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            user_state = UserState.get_user_by_id(user_id)
            if user_state:
                emit("response_player_finished_level", {"user_id": user_id}, to=room_id)

                if GameState.game_state_advance_ready(room_id=room_id):
                    emit("response_advance_level_confirmation", to=room_id)
                else:
                    user_state.add_score(300)
                    emit(
                        "response_score_update",
                        {
                            "user_id": user_id,
                            "score": user_state.score,
                            "rounds_won": user_state.rounds_won,
                        },
                        to=session["room_id"],
                    )
            else:
                emit("error", {"message": "Invalid UserState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("request_level_advance")
    def handle_level_advance(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            max_level = GameState.get_game_state_max_level_by_room(room_id)
            UserState.advance_user_state_current_level(user_id, max_level)

            user_state = UserState.get_user_by_id(user_id=user_id)
            if user_state:
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
                    to=room_id,
                )
            else:
                emit("error", {"message": "Invalid UserState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("request_game_finished")
    def handle_game_finished(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            game_state = GameState.get_game_state_by_room(room_id)
            user_state = UserState.get_user_by_id(user_id)
            if game_state and user_state:
                if game_state.both_players_completed_game():
                    game_state.update_round_winner()
                    if game_state.final_round():
                        game_state.set_status(Status.FINISHED.value)
                        game_state.update_game_winner()
                        emit(
                            "response_player_finished_all_rounds",
                            {
                                "user_id": user_id,
                                "winner_id": game_state.winner_id,
                            },
                            to=room_id,
                        )
                    else:
                        game_state.advance_next_round()
                        emit("response_maps_from_server", to=room_id)
                else:
                    emit("response_player_finished_game", {"user_id": user_id})
                    user_state.assign_level_bonus()
                emit("response_init_data_update", to=room_id)
            else:
                emit("error", {"message": "Invalid UserState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("request_data_update")
    def handle_data_update(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            user_state = UserState.get_user_by_id(user_id)
            game_state = GameState.get_game_state_by_room(room_id)
            if user_state and game_state:
                emit(
                    "response_score_update",
                    {
                        "user_id": user_state.user_id,
                        "score": user_state.score,
                        "rounds_won": user_state.rounds_won,
                    },
                    to=room_id,
                )
                emit(
                    "response_round_update",
                    {"round": game_state.current_round},
                    to=room_id,
                )
            else:
                emit("error", {"message": "Invalid UserState or GameState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("request_game_state_reset")
    def handle_game_state_reset(data) -> None:
        room_id = data.get("room_id")
        if room_id:
            game_state = GameState.get_game_state_by_room(room_id)
            if game_state:
                game_state.reset_game_state()
                emit("response_maps_from_server", to=room_id)
            else:
                emit("error", {"message": "Invalid GameState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("disconnect")
    def handle_disconnect(data) -> None:
        user_id = data.get("user_id")
        room_id = data.get("room_id")

        if user_id and room_id:
            game_state = GameState.get_game_state_by_room(room_id)
            if game_state:
                game_state.del_player(user_id)
                game_state.set_status(Status.JOIN_WAIT.value)
                print(f"Status print example: {Status.JOIN_WAIT.name}")

                print(f"Player {user_id} disconnected")
                leave_room(session["room_id"])
                session.pop("room_id", None)
                session.modified = True

                emit("response_player_disconnected", to=room_id)
            else:
                emit("error", {"message": "Invalid GameState."})
        else:
            emit("error", {"message": "Invalid session data."})

    @socketio.on("test_join_room")
    def handle_test_join_room(data):
        room = data.get("room_id")
        if room:
            join_room(room)
