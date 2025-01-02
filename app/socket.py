import json

from flask_socketio import emit, join_room
from typing import Dict

from app.types_validation import (
    RoomID,
    validate_room_in_db_emit,
    validate_socket_payload,
    RoomAndUserID,
    UserRoomIDKey,
    validate_user_in_db_emit,
)
from app.scripts.game import (
    get_position_from_map,
    user_state_update,
    validate_move,
)

from app.models.game_state_model import UserState, GameState
from app.enums import Status


def configure_socketio(socketio):
    """Configures socketio events."""

    @socketio.on("join_room")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    def handle_join_room(data: Dict) -> None:
        """Handles join room event."""
        room_id = data.get("room_id")
        user_id = data.get("user_id")

        join_room(room_id)
        game_state = GameState.get_game_state_by_room(room_id)

        if game_state.user_not_in_room(user_id) and game_state.room_is_available():
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

    @socketio.on("request_maps_from_server")
    @validate_socket_payload(RoomID)
    def handle_maps_from_server(data: Dict) -> None:
        """Handles request maps from server event."""
        room = data.get("room_id")
        emit("response_maps_from_server", to=room)

    @socketio.on("request_initial_maps")
    @validate_socket_payload(RoomAndUserID)
    @validate_user_in_db_emit(UserState)
    @validate_room_in_db_emit(GameState)
    def get_initial_maps(data: Dict) -> None:
        """Handles request initial maps event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        user_state = UserState.get_user_by_id(user_id)
        game_state = GameState.get_game_state_by_room(room_id)

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
                "achieved_level": user_state.achieved_level,
            },
            to=room_id,
        )
        emit(
            "response_round_update",
            {"round": game_state.current_round, "level": game_state.level},
            to=room_id,
        )

    @socketio.on("request_update_data")
    @validate_socket_payload(UserRoomIDKey)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_update_values(data: Dict) -> None:
        """Handles request update data event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        key = data.get("key")

        max_level = GameState.get_game_state_max_level_by_room(room_id)
        orig_map = UserState.get_user_by_id(user_id=user_id).map
        user_state_update(key, user_id, max_level)

        user_state = UserState.get_user_by_id(user_id=user_id)
        game_state = GameState.get_game_state_by_room(room_id)
        updated_map = user_state.map

        if orig_map != updated_map:
            game_state.add_move_to_stack(
                user_id, json.loads(updated_map), key, user_state.score
            )
            my_oponent, oponent_data = game_state.get_oponent_move(user_id)

            if my_oponent and oponent_data:
                emit(
                    "response_update_my_oponent",
                    {
                        "map": my_oponent[0],
                        "user_id": user_id,
                        "key": my_oponent[1],
                        "score": my_oponent[2],
                    },
                )
                emit(
                    "response_update_oponent_data",
                    {
                        "map": oponent_data[0],
                        "user_id": user_id,
                        "key": key,
                        "score": oponent_data[2],
                    },
                    to=room_id,
                )

        if user_state.game_completed:
            handle_game_finished({"user_id": user_id, "room_id": room_id})
        elif user_state.level_completed:
            handle_level_advance_confirmation({"user_id": user_id, "room_id": room_id})

    @socketio.on("request_level_advance_confirmation")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_level_advance_confirmation(data) -> None:
        """Handles the request_level_advance_confirmation event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        user_state = UserState.get_user_by_id(user_id)

        emit("response_player_finished_level", {"user_id": user_id}, to=room_id)

        if GameState.game_state_advance_ready(room_id):
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
                to=room_id,
            )

    @socketio.on("request_level_advance")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_level_advance(data) -> None:
        """Handles the request_level_advance event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        max_level = GameState.get_game_state_max_level_by_room(room_id)
        game_state = GameState.get_game_state_by_room(room_id)
        game_state.reset_stacks()

        UserState.advance_user_state_current_level(user_id, max_level)

        user_state = UserState.get_user_by_id(user_id)
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

    @socketio.on("request_game_finished")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_game_finished(data) -> None:
        """Handles the request_game_finished event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        game_state = GameState.get_game_state_by_room(room_id)
        user_state = UserState.get_user_by_id(user_id)

        if game_state.both_players_completed_game():
            round_winner = game_state.update_round_winner()
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
                emit(
                    "response_both_players_finished_game",
                    {"round_winner": round_winner},
                    to=room_id,
                )

        else:
            emit("response_player_finished_game", {"user_id": user_id})
            user_state.assign_level_bonus()
        emit("response_init_data_update", to=room_id)

    @socketio.on("request_round_advance")
    def handle_round_advance(data):
        """Handles the request_round_advance event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        game_state = GameState.get_game_state_by_room(room_id)
        game_state.advance_next_round()
        emit("response_maps_from_server", to=room_id)

    @socketio.on("request_data_update")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_data_update(data) -> None:
        """Handles the request_data_update event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        user_state = UserState.get_user_by_id(user_id)
        game_state = GameState.get_game_state_by_room(room_id)

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
            {"round": game_state.current_round, "level": game_state.level},
            to=room_id,
        )

    @socketio.on("request_game_state_reset")
    @validate_socket_payload(RoomID)
    @validate_room_in_db_emit(GameState)
    def handle_game_state_reset(data) -> None:
        """Handles the request_game_state_reset event."""
        room_id = data.get("room_id")
        game_state = GameState.get_game_state_by_room(room_id)

        game_state.reset_game_state()
        emit("response_maps_from_server", to=room_id)

    @socketio.on("disconnect")
    @validate_socket_payload(RoomAndUserID)
    @validate_room_in_db_emit(GameState)
    @validate_user_in_db_emit(UserState)
    def handle_disconnect(data) -> None:
        """Handles the disconnect event."""
        user_id = data.get("user_id")
        room_id = data.get("room_id")
        game_state = GameState.get_game_state_by_room(room_id)

        game_state.del_player(user_id)
        game_state.set_status(Status.JOIN_WAIT.value)

        emit("response_player_disconnected", to=room_id)

    @socketio.on("test_join_room")
    @validate_socket_payload(RoomID)
    def handle_test_join_room(data):
        """Handles the test_join_room event."""
        room = data.get("room_id")
        if room:
            join_room(room)
