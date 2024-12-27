"""
This script initializes the extensions used in the Flask application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()
