from flask import Flask

from app.extensions import db, socketio
from app.socket import configure_socketio
from app.routes import main, singleplayer, multiplayer


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")
    app.register_blueprint(main)
    app.register_blueprint(singleplayer)
    app.register_blueprint(multiplayer)

    db.init_app(app)

    socketio.init_app(app)
    configure_socketio(socketio)

    return app
