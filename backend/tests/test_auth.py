import pytest
import uuid


def generate_user_data():
    unique_id = uuid.uuid4()
    return {
        "username": f"tester_{unique_id}",
        "email": f"test_{unique_id}@mail.com",
        "password": "Password123",
        "phone": "77777777777",
        "role": "student"
    }


def test_register_success(client):
    user_data = generate_user_data()

    response = client.post('/api/auth/register', json=user_data)

    assert response.status_code == 201, response.data

    data = response.get_json()
    assert data is not None
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate(client):
    user_data = generate_user_data()

    client.post('/api/auth/register', json=user_data)
    response = client.post('/api/auth/register', json=user_data)

    assert response.status_code in [400, 409], response.data


def test_login_success(client):
    user_data = generate_user_data()

    client.post('/api/auth/register', json=user_data)

    response = client.post('/api/auth/login', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })

    assert response.status_code == 200, response.data

    data = response.get_json()
    assert data is not None
    assert "access_token" in data


def test_login_wrong_password(client):
    user_data = generate_user_data()

    client.post('/api/auth/register', json=user_data)

    response = client.post('/api/auth/login', json={
        "email": user_data["email"],
        "password": "wrong_password"
    })

    assert response.status_code == 401, response.data


def test_refresh_token(client):
    user_data = generate_user_data()

    res = client.post('/api/auth/register', json=user_data)

    assert res.status_code == 201, res.data

    tokens = res.get_json()
    assert tokens is not None
    assert "refresh_token" in tokens

    refresh_token = tokens['refresh_token']

    response = client.post('/api/auth/refresh', headers={
        "Authorization": f"Bearer {refresh_token}"
    })

    assert response.status_code == 200, response.data

    data = response.get_json()
    assert data is not None
    assert "access_token" in data


def test_login_no_user(client):
    response = client.post('/api/auth/login', json={
        "email": "nobody_exists@mail.com",
        "password": "123"
    })

    assert response.status_code == 401, response.data


def test_unauthorized_access(client):
    response = client.get('/api/lessons/topics')

    assert response.status_code == 401, response.data