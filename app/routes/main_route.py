from flask import (
    render_template,
    Blueprint,
)

from app.scripts.game import create_maps

main = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """
    Renders homepage.
    Creates maps database data.
    """
    create_maps()

    return render_template("home.html")


test_main = Blueprint("test_main", __name__)


@test_main.route("/")
def test_home() -> str:
    """
    Renders test homepage.
    """

    return render_template("home.html")
