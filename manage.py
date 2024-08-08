from app import create_app
from app.extensions import socketio, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", debug=True, port=8000)
