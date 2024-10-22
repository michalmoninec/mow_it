from app import create_app

app = create_app()


def test_home():
    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200
