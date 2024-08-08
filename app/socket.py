from flask import session
from flask_socketio import emit
from .scripts.game import game_update

def configure_socketio(socketio):
    @socketio.on("joined")
    def handle_connect():
        player_id = session["player_id"]
        emit("retrieve_map", {"map": session["map"], "player_id": player_id})
        

    @socketio.on("connect")
    def handle_connect():
        print(session["map"][1][0])
        print("somebody connected")


    @socketio.on("disconnect")
    def handle_disconnect():
        player_id = session.get("player_id")
        print(f'Session map before disconecting: {session['map'][2][0]}')
        print(f"Player {player_id} disconnected")


    @socketio.on("update_values")
    def update(data):
        player_id = session["player_id"]
        key = data["key"]
        game_update(key, session)
        print(session["map"][1][0])
        emit("update_grid", {"map": session["map"], "player_id": player_id}, broadcast=True)
