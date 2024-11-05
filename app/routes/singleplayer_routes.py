import uuid, json

from flask import (
    render_template,
    jsonify,
    session,
    request,
    Blueprint,
    Response,
)

from app.models.user_model import UserState

from app.scripts.game import (
    user_get_achieved_levels,
    user_state_update,
)


singleplayer = Blueprint("singleplayer", __name__)


@singleplayer.get("/single_player/level_selection/")
def single_player_level_selection() -> str:
    """Render page for level selection"""
    return render_template("single_player_level_selection.html")


@singleplayer.post("/single_player/level_data/")
def single_player_level_data() -> Response:
    """Prepare level based on user's achieved level"""

    data = request.get_json()

    try:
        user_id = data["user_id"]
    except KeyError:
        return jsonify({"message": "UserID not included."})

    if "user_id" not in session:
        if user_id:
            session["user_id"] = user_id
        else:
            session["user_id"] = str(uuid.uuid4())[:8]
        if not UserState.get_user_by_id(session["user_id"]):
            UserState.create_user_state(user_id=session["user_id"])

    try:
        levels = user_get_achieved_levels(session["user_id"])
    except:
        return jsonify({"message": "User or map not found."}), 404

    return jsonify({"user_id": session["user_id"], "levels": levels}), 200


@singleplayer.post("/single_player/selected_level/")
def single_player_set_selected_level() -> Response:
    desired_level = request.get_json().get("selected_level")

    if not desired_level:
        return jsonify({"message": "Desired level not provided."}), 400

    if "user_id" not in session:
        return jsonify({"message": "User or map not found."}), 400

    valid_level_set = UserState.get_user_by_id(session["user_id"]).set_desired_level(
        desired_level
    )

    return jsonify({"valid_level_set": valid_level_set}), 200


@singleplayer.post("/single_player/retrieve_map/")
def single_player_init_map() -> Response:
    """Returns prepared map when client connects, reloads, advance level"""

    user_id = request.get_json().get("user_id")

    if "user_id" not in session:
        if user_id:
            session["user_id"] = user_id
        else:
            session["user_id"] = str(uuid.uuid4())[:8]
        UserState.create_user_state(user_id=session["user_id"])

    user_state = UserState.get_user_by_id(session["user_id"])

    if user_state is None:
        return jsonify({"message": "User or map not found"}), 404

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


@singleplayer.get("/single_player/")
def single_player_prepare() -> str:
    """Render page for single player"""

    return render_template("single_player.html")


@singleplayer.post("/single_player/move/")
def single_player_move_handle() -> Response:
    """
    Receives key
    Updates game state
    """

    key = request.get_json().get("key")

    user_state_update(key, session["user_id"])
    user_state = UserState.get_user_by_id(session["user_id"])

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


@singleplayer.post("/single_player/advance_current_level/")
def single_player_advance_current_level() -> Response:
    """Increase user's level by 1 and redirect to game preparation"""

    valid_level_advance = UserState.advance_user_state_current_level(session["user_id"])

    return jsonify({"valid_advance": valid_level_advance})
