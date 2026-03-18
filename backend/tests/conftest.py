import pytest
import os
from app import create_app, db

@pytest.fixture
def app():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['FLASK_ENV'] = 'testing'
    
    _app = create_app()
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "BCRYPT_LOG_ROUNDS": 4,
        "JWT_SECRET_KEY": "test-secret-key"
    })

    with _app.app_context():
        db.drop_all()  
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()  

@pytest.fixture
def client(app):
    return app.test_client()