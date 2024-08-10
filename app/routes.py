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
from .scripts.game import (
    create_map,
    game_update,
    create_db_test_data,
    create_db_maps_data,
)


main = Blueprint("main", __name__)


@main.route("/")
def index():
    session.clear()
    return render_template("index.html")


@main.route("/single")
def single():
    # create_db_maps_data()
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

    if "score" not in session:
        session["score"] = 0

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

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())[:5]
        if "room_id" not in session:
            session["room_id"] = str(uuid.uuid4())[:5]
        create_db_test_data(room_id=session["room_id"], player_id=session["player_id"])

    # TODO - check if model exist with data above - player_id and room_id

    return redirect(url_for("main.game"))


# SLAMUS_NOTES - kokotske nazvy route melo by byt multiplayer_game nebo tak neco
@main.route("/game")
def game():
    if "player_id" not in session:
        return redirect(url_for("main.create_game"))

    game_state = GameState.query.filter_by(room_id=session["room_id"]).first()
    if session["player_id"] == game_state.player_1_id:
        map = json.loads(game_state.player_1_map)
        pos = json.loads(game_state.player_1_pos)
        score = game_state.player_1_score
    elif session["player_id"] == game_state.player_2_id:
        map = json.loads(game_state.player_2_map)
        pos = json.loads(game_state.player_2_pos)
        score = game_state.player_2_score

    session["map"] = map
    session["position"] = pos
    session["last_visited"] = pos
    session["score"] = score

    return render_template("multi_game.html")


@main.route("/game/<room_id>")
def join_game(room_id):
    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())[:5]

    db_room_id = GameState.query.filter_by(room_id=room_id).first()

    if db_room_id:
        if "room_id" not in session:
            session["room_id"] = room_id
    else:
        # TODO - add some message flashing to user, so they know room doesn exist.
        print(f"ROOM_ID not available.")
        return redirect(url_for("main.index"))

    if db_room_id.add_player(session["player_id"]):
        db.session.add(db_room_id)
        db.session.commit()
    else:
        # TODO - add message flash that room is full
        return redirect(url_for("main.index"))

    return redirect(url_for("main.game"))


@main.route("/versus_ai")
def versus():
    return render_template("versus_ai.html")
