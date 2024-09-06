from flask import (
    render_template,
    Blueprint,
)

from app.scripts.game import create_db_maps_data

main = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    """Renders homepage."""
    create_db_maps_data()

    return render_template("home.html")
