import uuid, json

from flask import (
    render_template,
    jsonify,
    session,
    request,
    Blueprint,
    Response,
)


from app.models import (
    create_user_state,
    get_user_by_id,
)
from app.scripts.game import (
    game_get_achieved_levels,
    game_state_advance_current_level,
    game_state_update,
)


singleplayer = Blueprint("singleplayer", __name__)


@singleplayer.route("/single_player")
def single_player_prepare() -> str:
    """Render page for single player"""

    return render_template("single_player.html")


@singleplayer.route("/single_player/level_selection")
def single_player_level_selection() -> str:
    """Render page for level selection"""
    # for creating data into database when deleting db
    # create_db_maps_data()
    return render_template("single_player_level_selection.html")


@singleplayer.route("/single_player/level_data", methods=["POST"])
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

    levels = game_get_achieved_levels(session["user_id"])

    return jsonify({"user_id": session["user_id"], "levels": levels})


@singleplayer.route("/single_player/selected_level", methods=["POST"])
def single_player_set_selected_level() -> Response:
    desired_level = request.get_json().get("selected_level")

    if "user_id" not in session:
        return jsonify({"error": "User or map not found"}), 404

    get_user_by_id(session["user_id"]).set_desired_level(desired_level)

    return jsonify({})


@singleplayer.route("/single_player/retrieve_map", methods=["POST", "GET"])
def single_player_init_map() -> Response:
    """Returns prepared map when client connects, reloads, advance level"""

    user_state = get_user_by_id(session["user_id"])

    if user_state is None:
        return jsonify({"error": "User or map not found"}), 404

    user_state.set_default_state_by_level()

    return jsonify(
        {
            "user_state": {
                "map": json.loads(user_state.map),
                "score": user_state.score,
                "completed": user_state.level_completed,
                "level": user_state.level,
            },
            "user_id": session["user_id"],
        }
    )


@singleplayer.route("/single_player/move", methods=["POST"])
def single_player_move_handle() -> Response:
    """
    Receives key
    Updates game state
    """

    key = request.get_json().get("key")

    game_state_update(key, session["user_id"])
    user_state = get_user_by_id(session["user_id"])

    return jsonify(
        {
            "user_state": {
                "map": json.loads(user_state.map),
                "score": user_state.score,
                "completed": user_state.level_completed,
                "game_completed": user_state.game_completed,
                "level": user_state.level,
            }
        }
    )


@singleplayer.route("/single_player/advance_current_level", methods=["POST"])
def single_player_advance_current_level() -> Response:
    """Increase user's level by 1 and redirect to game preparation"""

    game_state_advance_current_level(session["user_id"])

    return jsonify({})
