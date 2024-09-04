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
    Maps,
    GameState,
    UserState,
    create_user_after_room_join,
    create_user_state,
    get_user_by_id,
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


multiplayer = Blueprint("multiplayer", __name__)


@multiplayer.route("/multiplayer/create_game")
def multiplayer_level_selection() -> str:
    """Create multiplayer game"""
    return render_template("multiplayer_create_game.html")


@multiplayer.route("/multiplayer/create_game/room")
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


@multiplayer.route("/multiplayer_game")
def multiplayer_game() -> str | Response:
    """TODO"""

    if "player_id" not in session:
        return redirect(url_for("main.create_multiplayer_game"))

    return render_template("multiplayer_game.html")


@multiplayer.route("/multiplayer_game/<room_id>")
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
        db_room_id.status = Status.READY.value
        db.session.add(db_room_id)
        db.session.commit()
    else:
        print("Room does not exist, or is full.")
        return redirect(url_for("main.home"))

    return redirect(url_for("main.multiplayer_game"))
