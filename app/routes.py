import uuid, json

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    jsonify,
)

from .models import Maps, GameState
from .extensions import db
from .scripts.game import create_map, game_update, create_db_test_data


main = Blueprint("main", __name__)


@main.route("/")
def index():
    session.clear()
    return render_template("index.html")


@main.route("/single")
def single():

    map_db = Maps.query.filter_by(name="Hradec").first()
    map = json.loads(map_db.data)

    if "map" not in session:
        session["map"] = map

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

    return render_template("single.html")


@main.route("/single/ready", methods=["POST"])
def ready():
    return jsonify({"map": session["map"]})


@main.route("/single/move", methods=["POST"])
def move():
    key = request.get_json().get("key")

    game_update(key, session)

    return jsonify({"map": session["map"]})


@main.route("/create_game")
def create_game():

    # create_db_test_data()

    map_db = Maps.query.filter_by(name="Hradec").first()
    map = json.loads(map_db.data)

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())

    if "room_id" not in session:
        session["room_id"] = "room"

    if "map" not in session:
        session["map"] = map

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

    return redirect(url_for("main.game"))


@main.route("/game")
def game():
    return render_template("multi_game.html")


@main.route("/game/<room_id>")
def join_game(room_id):
    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())

    db_room_id = GameState.query.filter_by(room_id=room_id).first()

    if db_room_id:
        if "room_id" not in session:
            session["room_id"] = room_id
    else:
        print(f"ROOM_ID not available.")
        return redirect(url_for("main.index"))

    if "map" not in session:
        session["map"] = json.loads(db_room_id.map)

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

    return redirect(url_for("main.game"))


@main.route("/versus_ai")
def versus():
    return render_template("versus_ai.html")
