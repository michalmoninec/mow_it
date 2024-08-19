import uuid, json

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    Response,
    jsonify,
)

from .models import Maps, GameState
from .extensions import db
from .scripts.game import (
    create_map,
    game_state_update,
    create_db_game_state_data,
    create_db_maps_data,
)


main = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """Clears session data and renders homepage."""

    session.clear()
    return render_template("home.html")


@main.route("/single_player")
def single_player_prepare() -> str:
    """Render page for single player"""

    # for creating data into database when deleting db
    # create_db_maps_data()

    return render_template("single_player.html")


@main.route("/single_player/retrieve_map", methods=["POST"])
def single_player_init_map() -> Response:
    """Returns prepared map when client connects"""

    # level_name will be retrieved from front end via post method
    level_name = 1

    db_map = Maps.query.filter_by(level=level_name).first()
    if db_map is None:
        return jsonify({"error": "User not found"}), 404

    map = json.loads(db_map.data)
    pos = json.loads(db_map.start_position)
    score = 0

    return jsonify({"map": map, "pos": pos, "score": score})


@main.route("/single_player/move", methods=["POST"])
def single_player_move_handle() -> Response:
    """
    Validation of player move
    If valid, game state is updated and send to client
    """

    key = request.get_json().get("key")
    map = request.get_json().get("map")
    pos = request.get_json().get("pos")
    score = request.get_json().get("score")

    updated_game_state = game_state_update(key, map, pos, score)

    if updated_game_state:
        map = updated_game_state["map"]
        pos = updated_game_state["position"]
        score = updated_game_state["score"]

    return jsonify({"map": map, "pos": pos, "score": score})


@main.route("/create_multiplayer_game")
def create_multiplayer_game() -> Response:
    """TODO"""

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())[:5]
        if "room_id" not in session:
            session["room_id"] = str(uuid.uuid4())[:5]
        create_db_game_state_data(
            room_id=session["room_id"], player_id=session["player_id"]
        )

    # TODO - check if model exist with data above - player_id and room_id

    return redirect(url_for("main.multiplayer_game"))


# SLAMUS_NOTES - kokotske nazvy route melo by byt multiplayer_game nebo tak neco
@main.route("/multiplayer_game")
def multiplayer_game() -> str:
    """TODO"""

    if "player_id" not in session:
        return redirect(url_for("main.create_multiplayer_game"))

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

    return render_template("multiplayer_game.html")


@main.route("/game/<room_id>")
def join_game(room_id) -> Response:
    """TODO"""

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())[:5]

    db_room_id = GameState.query.filter_by(room_id=room_id).first()

    if db_room_id:
        if "room_id" not in session:
            session["room_id"] = room_id
    else:
        # TODO - add some message flashing to user, so they know room doesn exist.
        print(f"ROOM_ID not available.")
        return redirect(url_for("main.home"))

    if db_room_id.add_player(session["player_id"]):
        db.session.add(db_room_id)
        db.session.commit()
    else:
        # TODO - add message flash that room is full
        return redirect(url_for("main.home"))

    return redirect(url_for("main.multiplayer_game"))


@main.route("/versus_ai")
def versus() -> str:
    """TODO"""

    return render_template("versus_ai.html")
