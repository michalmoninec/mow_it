import pytest

from app import create_app


@pytest.fixture
def app_and_client():
    app = create_app()
    app.secret_key = "test_key_noodles"
    with app.test_client() as client:
        yield app, client
