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

from app.enums import Status
from app.models import (
    create_multiplayer_game_state,
    create_user_after_room_join,
    get_game_state_by_room,
)


multiplayer = Blueprint("multiplayer", __name__)


@multiplayer.route("/multiplayer/create_game")
def multiplayer_create_game() -> str:
    """Renders multiplayer game"""
    return render_template("multiplayer_create_game.html")


@multiplayer.route("/multiplayer/create_game/get_user_and_room", methods=["POST"])
def multiplayer_get_user() -> Response:

    user_id = request.get_json().get("user_id")
    if user_id:
        session["user_id"] = user_id
    else:
        session["user_id"] = str(uuid.uuid4())[:8]

    session["room_id"] = str(uuid.uuid4())[:8]

    return jsonify({"user_id": session["user_id"]})


@multiplayer.route("/multiplayer/create_game/room")
def create_multiplayer_game() -> Response:
    """
    Creates multiplayer game state.
    Redirects to multiplayer game with id in parameter.
    """

    create_multiplayer_game_state(session["room_id"], session["user_id"])

    return redirect(url_for("multiplayer.multiplayer_game_play"))


@multiplayer.route("/multiplayer_game/join_room/<room_id>")
def join_game(room_id) -> str:
    """
    Assigns room_id for client's session
    Renders page for joining room
    """

    session["room_id"] = room_id

    return render_template("multiplayer_join_room.html")


@multiplayer.route("/join_room/set_user_and_room", methods=["POST"])
def join_room_set_user_and_room() -> Response:
    user_id = request.get_json().get("user_id")
    try:
        room_id = session["room_id"]
    except Exception as e:
        print(e)

    if user_id:
        session["user_id"] = user_id
    else:
        session["user_id"] = str(uuid.uuid4())[:8]

    game_state = get_game_state_by_room(room_id)
    if game_state is None:
        print(f"ROOM_ID not available.")
        return redirect(url_for("main.home"))

    if game_state.user_not_in_room(session["user_id"]):
        if game_state.room_is_available():
            game_state.add_player(session["user_id"])
        else:
            print("Room is full.")
            return redirect(url_for("main.home"))

    create_user_after_room_join(
        session["room_id"],
        session["user_id"],
    )

    return jsonify({"user_id": session["user_id"]})


@multiplayer.route("/multiplayer_game/play")
def multiplayer_game_play():
    return render_template("multiplayer_game.html")
