import uuid, json

from flask import (
    render_template,
    redirect,
    url_for,
    session,
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
def multiplayer_level_selection() -> str:
    """Renders multiplayer game"""
    return render_template("multiplayer_create_game.html")


@multiplayer.route("/multiplayer/create_game/room")
def create_multiplayer_game() -> Response:
    """
    Sets flask session with user_id and room_id.
    Creates multiplayer game state.
    Redirects to multiplayer game with id in parameter.
    """

    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())[:8]

    session["room_id"] = str(uuid.uuid4())[:8]
    create_multiplayer_game_state(session["room_id"], session["user_id"])

    return redirect(url_for("multiplayer.join_game", room_id=session["room_id"]))


@multiplayer.route("/multiplayer_game/<room_id>")
def join_game(room_id) -> Response | str:
    """TODO"""
    if "user_id" not in session:
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

    session["room_id"] = room_id

    create_user_after_room_join(
        session["room_id"],
        session["user_id"],
    )

    return render_template("multiplayer_game.html")
