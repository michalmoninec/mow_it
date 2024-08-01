from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    jsonify,
    session,
    request,
)
from flask_socketio import SocketIO, emit, join_room, leave_room

import uuid
import json

from game import game_update

app = Flask(__name__)
app.config["SECRET_KEY"] = "kurecisecuan"
socketio = SocketIO(app)


players = []


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/single")
def single():
    p_map = create_map()
    p_map[0][0]["active"] = True

    if "map" not in session:
        session["map"] = p_map

    if "position" not in session:
        session["position"] = {
            "x": 0,
            "y": 0,
        }

    if "last_visited" not in session:
        session["last_visited"] = {
            "x": 0,
            "y": 0,
        }
    # print(f'session on slash single is {session}')
    return render_template("single.html", player_map=session["map"])


@app.route("/single/move", methods=["POST"])
def move():
    key = request.get_json().get("key")

    game_update(key, session)

    return jsonify({"map": session["map"]})


@app.route("/create_game")
def create_game():
    # room_id = str(uuid.uuid4())
    # player_id = session.get("player_id")
    p_map = create_map()
    p_map[0][0]["active"] = True

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())

    if "map" not in session:
        session["map"] = p_map

    if "position" not in session:
        session["position"] = {
            "x": 0,
            "y": 0,
        }

    if "last_visited" not in session:
        session["last_visited"] = {
            "x": 0,
            "y": 0,
        }

    return redirect(url_for("game"))


@app.route("/game")
def game():
    player_id = session.get("player_id")
    print(f"player id in game: {player_id}")
    return render_template(
        "multi_game.html", player_id=player_id, players=players, map=session["map"]
    )


@app.route("/versus_ai")
def versus():
    return render_template("versus_ai.html")


@socketio.on("joined")
def handle_connect():
    player_id = session.get("player_id")
    print(f"Players in `handle connect`: {players}")
    players.append(player_id)
    print(f"Player {player_id} connected")
    emit("players", {"players": players}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    player_id = session.get("player_id")
    if player_id in players:
        players.remove(player_id)
    emit("players", {"players": players}, broadcast=True)
    print(f"Player {player_id} disconnected")


@socketio.on("update_values")
def update(data):
    player_id = session["player_id"]
    key = data["key"]
    game_update(key, session)
    emit("update_grid", {"map": session["map"], "player_id": player_id}, broadcast=True)


def create_map():
    map = []
    for col in range(10):
        col_cell = []
        for row in range(10):
            cell = {
                "x": col,
                "y": row,
                "active": False,
                "blocker": False,
                "visited": False,
            }
            col_cell.append(cell)
        map.append(col_cell)
    return map


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True, port=8000)
