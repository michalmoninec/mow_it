class Config:
    SECRET_KEY = "aasdqweoriuqpwoeiu"
    SQLALCHEMY_DATABASE_URI = "sqlite:///map.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SECRET_KEY = "aasdqweoriuqpwoeiu"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
