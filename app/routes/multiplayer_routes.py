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

from app.enums import Status
from app.models import (
    create_multiplayer_game_state,
    create_user_after_room_join,
    get_game_state_by_room,
)


multiplayer = Blueprint("multiplayer", __name__)


@multiplayer.route("/multiplayer/creation")
def multiplayer_create_game() -> str:
    """Renders multiplayer game"""
    print(f"sess in creation: {session}")
    return render_template("multiplayer_create_game.html")


@multiplayer.route("/multiplayer/create_game", methods=["POST"])
def multiplayer_get_user() -> Response:
    """
    Gets ID from client, if id is None, then it assign new random ID.
    Assign random room_id.
    Returns user_id either from client or newly assigned.
    """
    print("it gets redirected to creation")
    user_id = request.get_json().get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    session["user_id"] = user_id
    session["room_id"] = str(uuid.uuid4())[:8]

    create_multiplayer_game_state(session["room_id"])

    return jsonify({"user_id": session["user_id"], "room_id": session["room_id"]})


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
        return redirect(url_for("main.home"))

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    session["user_id"] = user_id

    game_state = get_game_state_by_room(room_id)
    if game_state is None:
        session["room_id"] = None
    elif (
        game_state.user_not_in_room(session["user_id"])
        and not game_state.room_is_available()
    ):
        session["room_id"] = None
    else:
        create_user_after_room_join(
            session["room_id"],
            session["user_id"],
        )

    return jsonify({"user_id": session["user_id"], "room_id": session["room_id"]})


@multiplayer.route("/multiplayer_game/play")
def multiplayer_game_play() -> str:
    print(f"session at play: {session}")
    if "user_id" in session and "room_id" in session:
        print("user or room id is none")
        return render_template("multiplayer_game.html")
    return redirect(url_for("multiplayer.multiplayer_create_game"))
