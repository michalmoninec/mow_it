import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    jsonify,
)

from .models import Maps
from .scripts.game import create_map, game_update


main = Blueprint("main", __name__)


@main.route("/")
def index():
    session.clear()
    return render_template("index.html")


@main.route("/single")
def single():
    p_map = create_map()
    # p_map[0][0]["active"] = True

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
    # room_id = str(uuid.uuid4())
    # player_id = session.get("player_id")
    p_map = create_map()
    # db_create_map()
    found_map = Maps.query.filter_by(name="Hradec").first()
    print(f"found map in db is: {found_map.size}")
    # p_map[0][0]["active"] = True

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

    return redirect(url_for("main.game"))


@main.route("/game")
def game():
    # player_id = session.get("player_id")
    # print(f"player id in game: {player_id}")

    return render_template("multi_game.html")


@main.route("/versus_ai")
def versus():
    return render_template("versus_ai.html")
