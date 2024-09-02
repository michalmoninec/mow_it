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
    create_user_after_room_join,
    create_user_state,
    reset_user_state_level,
    set_user_state_level,
)
from app.extensions import db
from app.scripts.game import (
    game_get_achieved_levels,
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

    return render_template("single_player.html")


@main.route("/single_player/level_selection")
def single_player_level_selection() -> str:
    """Render page for level selection"""
    # for creating data into database when deleting db
    # create_db_maps_data()
    return render_template("single_player_level_selection.html")


@main.route("/single_player/level_data", methods=["POST"])
def single_player_level_data() -> Response:
    """Prepare level based on user's achieved level"""

    user_id = request.get_json().get("user_id")

    if "user_id" not in session:
        if user_id:
            session["user_id"] = user_id
            create_user_state(user_id=session["user_id"])
        else:
            session["user_id"] = str(uuid.uuid4())[:8]
            create_user_state(user_id=session["user_id"])

    levels = game_get_achieved_levels(user_id=session["user_id"])
    # print(f"levels are: {levels}")

    return jsonify({"user_id": session["user_id"], "levels": levels})


@main.route("/single_player/selected_level", methods=["POST"])
def single_player_set_selected_level() -> Response:
    desired_level = request.get_json().get("selected_level")

    if "user_id" not in session:
        return jsonify({"error": "User or map not found"}), 404

    achieved_level = (
        UserState.query.filter_by(user_id=session["user_id"]).first().achieved_level
    )

    if desired_level <= achieved_level:
        set_user_state_level(user_id=session["user_id"], level=desired_level)

    print(f"desired level is: {desired_level}")
    return jsonify({"level": "ok"})


@main.route("/single_player/retrieve_map", methods=["POST", "GET"])
def single_player_init_map() -> Response:
    """Returns prepared map when client connects"""

    if "user_id" not in session:
        return jsonify({"error": "User or map not found"}), 404

    game_state = game_state_creation(user_id=session["user_id"])

    if game_state is None:
        return jsonify({"error": "User or map not found"}), 404

    return jsonify({"game_state": game_state, "user_id": session["user_id"]})


@main.route("/single_player/move", methods=["POST"])
def single_player_move_handle() -> Response:
    """
    Receives key
    Updates game state
    For valid move, updates game state
    """

    key = request.get_json().get("key")

    updated_game_state = game_state_update(key, user_id=session["user_id"])

    return jsonify({"game_state": updated_game_state})


@main.route("/single_player/advance_current_level", methods=["POST"])
def single_player_advance_current_level() -> Response:
    """Increase user's level by 1 and redirect to game preparation"""

    game_state_advance_current_level(user_id=session["user_id"])

    return jsonify({"level_reset": True})


@main.route("/multiplayer/create_game")
def multiplayer_level_selection() -> str:
    """Create multiplayer game"""
    return render_template("multiplayer_create_game.html")


@main.route("/multiplayer/create_game/room")
def create_multiplayer_game() -> Response:
    """TODO"""

    if "player_id" not in session:
        session["player_id"] = str(uuid.uuid4())[:8]
        if "room_id" not in session:
            session["room_id"] = str(uuid.uuid4())[:8]
        create_db_game_state_data(
            room_id=session["room_id"], player_id=session["player_id"]
        )

    return redirect(url_for("main.multiplayer_game"))


@main.route("/multiplayer_game")
def multiplayer_game() -> str | Response:
    """TODO"""

    if "player_id" not in session:
        return redirect(url_for("main.create_multiplayer_game"))

    return render_template("multiplayer_game.html")


@main.route("/multiplayer_game/<room_id>")
def join_game(room_id) -> Response:
    """TODO"""

    db_room_id = GameState.query.filter_by(room_id=room_id).first()

    if db_room_id:
        session["room_id"] = room_id
    else:
        # TODO - add some message flashing to user, so they know room doesn exist.
        print(f"ROOM_ID not available.")
        return redirect(url_for("main.home"))

    session["player_id"] = str(uuid.uuid4())[:8]
    create_user_after_room_join(
        room_id=room_id,
        player_id=session["player_id"],
    )

    # TODO - change it to function at models module
    if db_room_id.add_player(session["player_id"]):
        db.session.add(db_room_id)
        db.session.commit()
    else:
        print("Room does not exist, or is full.")
        return redirect(url_for("main.home"))

    return redirect(url_for("main.multiplayer_game"))
