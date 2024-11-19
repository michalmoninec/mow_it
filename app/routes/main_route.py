from flask import (
    render_template,
    Blueprint,
    session,
)

from app.scripts.game import create_maps

main = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """
    Renders homepage.
    Creates maps database data.
    Clears session.
    """
    create_maps()

    return render_template("home.html")
