from flask import Flask


from app.extensions import db, socketio
from app.socket import configure_socketio
from app.routes import main, test_main, singleplayer, multiplayer


def create_app(config_class="config.Config") -> Flask:
    """Creates Flask app, register blueprints and configure socketio."""
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.register_blueprint(main)
    app.register_blueprint(singleplayer)
    app.register_blueprint(multiplayer)

    db.init_app(app)

    socketio.init_app(app, manage_session=True, cors_allowed_origins="*")
    configure_socketio(socketio)

    return app


def test_app(config_class="config.TestConfig") -> Flask:
    """Creates test Flask app, register blueprints, where main
    is different, due to map_table creation.
    Socketio is not configured here, it is configured inside test fixture.
    """
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.register_blueprint(test_main)
    app.register_blueprint(singleplayer)
    app.register_blueprint(multiplayer)

    db.init_app(app)
    return app


app = create_app()
