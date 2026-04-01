import pytest
from seed import run_seed

@pytest.fixture(autouse=True)
def setup_test_data(app):
    with app.app_context():
        run_seed(app)

@pytest.fixture
def auth_headers(client):
    user_data = {
        "username": "student_test",
        "email": "student_final@chess.com",
        "password": "Password123",
        "phone": "87071234567"
    }
    client.post('/api/auth/register', json=user_data)
    login_res = client.post('/api/auth/login', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_res.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_get_topics(client, auth_headers):
    response = client.get('/api/lessons/topics', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json['topics']) == 5
    assert response.json['topics'][0]['name'] == "Основы"

def test_get_lessons_filter(client, auth_headers):
    response = client.get('/api/lessons/?topic_id=1', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json['lessons']) == 3

def test_get_single_lesson_full(client, auth_headers):
    response = client.get('/api/lessons/1', headers=auth_headers)
    assert response.status_code == 200
    assert 'theory_cards' in response.json['lesson']
    assert response.json['lesson']['id'] == 1

def test_get_exercises_list(client, auth_headers):
    response = client.get('/api/lessons/1/exercises', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json['exercises'], list)
    if len(response.json['exercises']) > 0:
        assert 'correct_move' not in response.json['exercises'][0]

def test_check_exercise_correct(client, auth_headers):
    data = {"move": "Qxe8#"}
    response = client.post('/api/lessons/1/exercises/1/check', json=data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['is_correct'] is True

def test_check_exercise_wrong(client, auth_headers):
    data = {"move": "e2e4"}
    response = client.post('/api/lessons/1/exercises/1/check', json=data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['is_correct'] is False
    assert 'hint' in response.json

def test_complete_lesson(client, auth_headers):
    response = client.post('/api/lessons/1/complete', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Урок завершён'

def test_lessons_unauthorized(client):
    response = client.get('/api/lessons/topics')
    assert response.status_code == 401