from app import create_app
from app.extensions import db

# Create the app instance
app = create_app()

with app.app_context():
    db.create_all()  # This creates all tables defined in your SQLAlchemy models
    print("Tables created successfully!")
