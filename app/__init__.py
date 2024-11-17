from flask import Flask
from flask_session import Session

from redis import Redis

from app.extensions import db, socketio
from app.socket import configure_socketio
from app.routes import main, singleplayer, multiplayer


def create_app(config_class="config.Config") -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.register_blueprint(main)
    app.register_blueprint(singleplayer)
    app.register_blueprint(multiplayer)

    db.init_app(app)

    socketio.init_app(app, manage_session=True)
    configure_socketio(socketio)

    return app


def test_app(config_class="config.TestConfig") -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.register_blueprint(main)
    app.register_blueprint(singleplayer)
    app.register_blueprint(multiplayer)

    db.init_app(app)
    return app
