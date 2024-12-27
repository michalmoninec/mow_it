"""
This script runs the Flask application using SocketIO locally.
"""

from app import create_app
from app.extensions import socketio, db
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(
        app,
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        debug=os.getenv("FLASK_DEBUG", "True") == "True",
        port=int(os.getenv("FLASK_RUN_PORT", 8000)),
    )
