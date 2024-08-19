import json

from flask import session
from flask_socketio import emit, join_room
from .scripts.game import game_state_update
from .models import GameState

from app.extensions import db


def configure_socketio(socketio):
    @socketio.on("joined")
    def handle_connect():
        player_id = session["player_id"]
        map = session["map"]
        room = session["room_id"]

        join_room(room)
        print(f"Joined room: {room}")

        game_state = GameState.query.filter_by(room_id=session["room_id"]).first()
        map_1 = json.loads(game_state.player_1_map)
        map_2 = json.loads(game_state.player_2_map)

        emit(
            "retrieve_player_id",
            {"player_id": session["player_id"], "map_1": map_1, "map_2": map_2},
        )

        emit(
            "update_grid",
            {"map": session["map"], "player_id": player_id},
            broadcast=True,
        )

    @socketio.on("connect")
    def handle_connect():
        print("somebody connected")
        # emit("connect", {"player_id": session["player_id"]})

    @socketio.on("disconnect")
    def handle_disconnect():
        player_id = session.get("player_id")

        print(f"Player {player_id} disconnected")

    @socketio.on("update_values")
    def update(data):
        player_id = session["player_id"]
        key = data["key"]

        game_state_update(key, session)
        print(f'Updated score is: {session["score"]}')

        game_state = GameState.query.filter_by(room_id=session["room_id"]).first()
        if session["player_id"] == game_state.player_1_id:
            game_state.player_1_map = json.dumps(session["map"])
            game_state.player_1_pos = json.dumps(session["position"])
            game_state.player_1_score = session["score"]
        elif session["player_id"] == game_state.player_2_id:
            game_state.player_2_map = json.dumps(session["map"])
            game_state.player_2_pos = json.dumps(session["position"])
            game_state.player_2_score = session["score"]
        db.session.add(game_state)
        db.session.commit()

        emit(
            "update_grid",
            {"map": session["map"], "player_id": player_id},
            broadcast=True,
        )
