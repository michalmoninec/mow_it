import uuid

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

from app.models.game_state_model import GameState


multiplayer = Blueprint("multiplayer", __name__)


@multiplayer.get("/multiplayer/create/")
def multiplayer_create_game() -> str:
    """Renders multiplayer game"""
    return render_template("multiplayer_create_game.html")


@multiplayer.post("/multiplayer/create/")
def multiplayer_get_user() -> Response:
    """
    Gets ID from client, if id is None, then it assign new random ID.
    Assign random room_id.
    Returns user_id either from client or newly assigned.
    """
    request_data = request.get_json()
    user_id = request_data["user_id"]

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    session["user_id"] = user_id
    session["room_id"] = str(uuid.uuid4())[:8]

    GameState.create_multiplayer_game_state(session["room_id"])
    GameState.create_user_after_room_join(session["room_id"], session["user_id"])

    return jsonify({"user_id": session["user_id"], "room_id": session["room_id"]}), 201


@multiplayer.get("/multiplayer/join/<room_id>/")
def join_room_get_user(room_id) -> str:
    return render_template("multiplayer_join_room.html", room_id=room_id)


@multiplayer.post("/multiplayer/join/<room_id>/")
def join_room_set_user_and_room(room_id) -> Response:
    user_id = request.get_json().get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    session["user_id"] = user_id
    session["room_id"] = room_id

    game_state = GameState.get_game_state_by_room(room_id)
    if game_state is None:
        session["room_id"] = None
    elif (
        game_state.user_not_in_room(session["user_id"])
        and not game_state.room_is_available()
    ):
        session["room_id"] = None
    else:
        GameState.create_user_after_room_join(
            session["room_id"],
            session["user_id"],
        )

    return jsonify({"user_id": session["user_id"], "room_id": session["room_id"]}), 201


@multiplayer.get("/multiplayer/play/")
def multiplayer_game_play() -> str:
    print(f"session at play: {session}")
    if "user_id" in session and "room_id" in session:
        print("user or room id is none")
        return render_template("multiplayer_game.html")
    return redirect(url_for("multiplayer.multiplayer_create_game"))
