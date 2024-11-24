import uuid

from flask import (
    render_template,
    jsonify,
    Blueprint,
    Response,
)
from app.models.user_model import UserState
from app.types_validation import (
    UserID,
    RoomAndUserID,
    validate_json,
    validate_room_in_db,
    validate_user_in_db,
)
from app.models.game_state_model import GameState


multiplayer = Blueprint("multiplayer", __name__)


@multiplayer.get("/multiplayer/create/")
def multiplayer_create_game() -> str:
    """Renders multiplayer game"""
    return render_template("multiplayer_create_game.html")


@multiplayer.post("/multiplayer/create/")
@validate_json(UserID)
def multiplayer_get_user(data) -> Response:
    """
    Gets ID from client, if id is None, then it assign new random ID.
    Assign random room_id.
    Returns user_id either from client or newly assigned.
    """
    user_id = data["user_id"]
    room_id = str(uuid.uuid4())[:8]

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    GameState.create_multiplayer_game_state(room_id)
    GameState.create_user_after_room_join(room_id, user_id)

    return jsonify({"user_id": user_id, "room_id": room_id}), 201


@multiplayer.get("/multiplayer/join/<room_id>/")
def join_room_get_user(room_id) -> str:
    """
    Renders page and passes room_id parameter.
    """
    return render_template("multiplayer_join_room.html", room_id=room_id), 200


@multiplayer.post("/multiplayer/join/<room_id>/")
@validate_json(UserID)
def join_room_set_user_and_room(data, room_id) -> Response:
    """
    Handles joining room.
    If neccesarry, creates new User.
    If provided room_id doesn't exist, or is full, return bad request status code.
    If valid room_id, returns user and room ID as confirmation.
    """
    user_id = data["user_id"]

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    game_state = GameState.get_game_state_by_room(room_id)

    if game_state is None:
        return jsonify({"error": "Invalid room ID."}), 400
    elif game_state.user_not_in_room(user_id) and not game_state.room_is_available():
        return jsonify({"error": "Room is full."}), 400
    else:
        GameState.create_user_after_room_join(
            room_id,
            user_id,
        )

    return jsonify({"user_id": user_id, "room_id": room_id}), 201


@multiplayer.get("/multiplayer/play/")
def multiplayer_game_play() -> str:
    """
    Renders page for multiplayer game.
    """
    return render_template("multiplayer_game.html"), 200


@multiplayer.post("/multiplayer/play/")
@validate_json(RoomAndUserID)
@validate_user_in_db(UserState)
@validate_room_in_db(GameState)
def multiplayer_game_play_fetch(data) -> str:
    """
    Checks, wether user and room ID correspond with user and room in db.
    If not, return validity with False value.
    Otherwise retusn validity with True value.
    """
    user_id = data["user_id"]
    room_id = data["room_id"]
    if user_id and room_id:
        return jsonify({"valid": True})
    return jsonify({"valid": False})
