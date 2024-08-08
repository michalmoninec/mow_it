from flask import Flask

from .extensions import db, socketio
from .socket import configure_socketio
from .routes import main


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")
    app.register_blueprint(main)

    db.init_app(app)

    socketio.init_app(app)
    configure_socketio(socketio)

    return app
