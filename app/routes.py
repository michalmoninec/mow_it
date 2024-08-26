import uuid, json

from flask import (
    render_template,
    redirect,
    url_for,
    jsonify,
    session,
    request,
    Blueprint,
    Response,
)

from app.models import (
    Maps,
    GameState,
    UserState,
    create_user_state,
    reset_user_state_level,
)
from app.extensions import db
from app.scripts.game import (
    game_state_advance_current_level,
    game_state_creation,
    game_state_update,
    create_db_game_state_data,
    create_db_maps_data,
)


main = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """Clears session data and renders homepage."""

    # session.clear()
    return render_template("home.html")


@main.route("/single_player")
def single_player_prepare() -> str:
    """Render page for single player"""

    # for creating data into database when deleting db
    # create_db_maps_data()

    return render_template("single_player.html")


@main.route("/single_player/level_selection")
def single_player_level_selection() -> str:
    return render_template("single_player_level_selection.html")


@main.route("/single_player/retrieve_map", methods=["POST", "GET"])
def single_player_init_map() -> Response:
    """Returns prepared map when client connects"""

    user_id = request.get_json().get("user_id")

    if "user_id" not in session:
        if user_id:
            session["user_id"] = user_id
        else:
            session["user_id"] = str(uuid.uuid4())[:8]
            create_user_state(user_id=session["user_id"])

    game_state = game_state_creation(user_id=session["user_id"])

    if game_state is None:
        return jsonify({"error": "User or map not found"}), 404

    return jsonify({"game_state": game_state, "user_id": session["user_id"]})


@main.route("/single_player/move", methods=["POST"])
def single_player_move_handle() -> Response:
    """
    Gets move, map, pos and score from client,
    Updates game state
    If move is valid, send updated state, otherwise state is not changed
    """

    data = request.get_json()
    key = data.get("key")
    map = data.get("map")
    pos = data.get("pos")
    score = data.get("score")

    updated_game_state = game_state_update(
        key, map, pos, score, user_id=session["user_id"]
    )

    return jsonify({"game_state": updated_game_state})


@main.route("/single_player_reset_level")
def single_player_reset_level() -> Response:
    """Reset user's level to 1 and redirect to game preparation"""

    reset_user_state_level(user_id=session["user_id"])

    return redirect(url_for("main.single_player_prepare"))


@main.route("/single_player/advance_current_level", methods=["POST"])
def single_player_advance_current_level() -> Response:
    """Decrease user's level by 1 and redirect to game preparation"""

    game_state_advance_current_level(user_id=session["user_id"])

    return jsonify({"level_reset": True})


@main.route("/multiplayer/level_selection")
def multiplayer_level_selection() -> str:
    return render_template("multiplayer_level_selection.html")


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


@main.route("/levels_completed")
def levels_completed():
    return render_template("single_levels_completed.html")


@main.route("/versus_ai")
def versus() -> str:
    """TODO"""

    return render_template("versus_ai.html")


@main.route("/map_creation")
def map_creation() -> str:
    return render_template("create_map.html")
