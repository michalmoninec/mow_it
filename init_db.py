"""
This script initializes the database for the Flask application.
"""

from app import create_app
from app.extensions import db

app = create_app()

try:
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")
except Exception as e:
    print(f"An error occurred while initializing the database: {e}")
