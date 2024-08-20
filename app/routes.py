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

from app.models import Maps, GameState, UserState
from app.extensions import db
from app.scripts.game import (
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
    create_db_maps_data()

    return render_template("single_player.html")


@main.route("/single_player/retrieve_map", methods=["POST"])
def single_player_init_map() -> Response:
    """Returns prepared map when client connects"""

    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())[:8]
        user_state = UserState(user_id=session["user_id"], level=1)
        db.session.add(user_state)
        db.session.commit()

    user_state = UserState.query.filter_by(user_id=session["user_id"]).first()

    level = user_state.level

    if level > 3:
        level = 3
        return jsonify({"levels_completed": True})

    db_map = Maps.query.filter_by(level=level).first()
    if db_map is None:
        return jsonify({"error": "User not found"}), 404

    map = json.loads(db_map.data)
    pos = json.loads(db_map.start_position)
    score = 0
    completed = False

    return jsonify({"map": map, "pos": pos, "score": score, "completed": completed})


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
        completed = updated_game_state["completed"]
    else:
        completed = False

    if completed:
        user_state = UserState.query.filter_by(user_id=session["user_id"]).first()
        # level = user_state.level
        user_state.level += 1
        if user_state.level > 3:
            return jsonify({"levels_completed": True})
        db.session.commit()

    return jsonify({"map": map, "pos": pos, "score": score, "completed": completed})


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
    return "<h1>CONGRATULATIONS, all levels completed.</h1>"


@main.route("/versus_ai")
def versus() -> str:
    """TODO"""

    return render_template("versus_ai.html")
