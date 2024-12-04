import uuid, json

from flask import (
    render_template,
    jsonify,
    Blueprint,
    Response,
)

from app.types_validation import (
    KeyAndUserID,
    UserID,
    LevelAndUserID,
    validate_json,
    validate_user_in_db,
)
from app.models.user_model import UserState

from app.scripts.game import (
    user_get_achieved_levels,
    user_state_update,
)


singleplayer = Blueprint("singleplayer", __name__)


@singleplayer.get("/single_player/level_selection/")
def single_player_level_selection() -> str:
    """Renders page for level selection."""
    return render_template("single_player_level_selection.html")


@singleplayer.post("/single_player/level_data/")
@validate_json(UserID)
def single_player_level_data(data) -> Response:
    """Prepare level based on user's achieved level."""
    user_id = data["user_id"]
    user_state = UserState.get_user_by_id(user_id)
    if user_state is None:
        user_id = str(uuid.uuid4())[:8]
        UserState.create_user_state(user_id)
    levels = user_get_achieved_levels(user_id)
    return jsonify({"user_id": user_id, "levels": levels}), 200


@singleplayer.post("/single_player/selected_level/")
@validate_json(LevelAndUserID)
@validate_user_in_db(UserState)
def single_player_set_selected_level(data) -> Response:
    """Receives desired level, validate the level with boundary to max achieved level
    and returns json with "valid_level_set" = True if level was set
    correctly, otherwise False.
    """
    user_id = data["user_id"]
    desired_level = data["selected_level"]
    user_state = UserState.get_user_by_id(user_id)
    valid_level_set = user_state.set_desired_level(desired_level)
    return jsonify({"valid_level_set": valid_level_set}), 200


@singleplayer.post("/single_player/retrieve_map/")
@validate_json(UserID)
@validate_user_in_db(UserState)
def single_player_init_map(data) -> Response:
    """Returns prepared map when client connects, reloads, advance level."""

    user_id = data["user_id"]

    if user_id is None:
        user_id = str(uuid.uuid4())[:8]
        UserState.create_user_state(user_id)

    user_state = UserState.get_user_by_id(user_id)
    user_state.set_default_state_by_level()

    return (
        jsonify(
            {
                "user_state": {
                    "map": json.loads(user_state.map),
                    "score": user_state.score,
                    "completed": user_state.level_completed,
                    "level": user_state.level,
                },
                "user_id": user_id,
            }
        ),
        200,
    )


@singleplayer.get("/single_player/")
def single_player_prepare() -> str:
    """Render page for single player."""

    return render_template("single_player.html")


@singleplayer.post("/single_player/move/")
@validate_json(KeyAndUserID)
@validate_user_in_db(UserState)
def single_player_move_handle(data) -> Response:
    """Receives key.
    Updates game state.
    """
    user_id = data["user_id"]
    key = data["key"]

    user_state = user_state_update(key, user_id)

    return (
        jsonify(
            {
                "user_state": {
                    "map": json.loads(user_state.map),
                    "score": user_state.score,
                    "completed": user_state.level_completed,
                    "game_completed": user_state.game_completed,
                    "level": user_state.level,
                }
            }
        ),
        200,
    )


@singleplayer.post("/single_player/advance_current_level/")
@validate_user_in_db(UserState)
@validate_json(UserID)
def single_player_advance_current_level(data) -> Response:
    """Increase user's level by 1 and redirect to game preparation."""
    user_id = data["user_id"]
    valid_level_advance = UserState.advance_user_state_current_level(user_id)

    return jsonify({"valid_advance": valid_level_advance}), 200
