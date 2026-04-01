import pytest
import uuid
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

@pytest.fixture
def admin_headers(app):
    with app.app_context():
        unique_id = uuid.uuid4().hex[:6]
        admin = User(
            username=f"admin_{unique_id}",
            email=f"admin_{unique_id}@chess.com",
            role="admin"
        )
        admin.set_password("adminpassword")
        db.session.add(admin)
        db.session.commit()
        token = create_access_token(identity=str(admin.id))
        return {"Authorization": f"Bearer {token}"}

# --- USERS ---

def test_get_users_list(client, admin_headers):
    response = client.get('/api/admin/users', headers=admin_headers)
    assert response.status_code == 200
    assert 'users' in response.get_json()
    assert isinstance(response.get_json()['users'], list)

def test_get_user_detail(client, admin_headers):
    users_data = client.get('/api/admin/users', headers=admin_headers).get_json()
    user_id = users_data['users'][0]['id']
    response = client.get(f'/api/admin/users/{user_id}', headers=admin_headers)
    assert response.status_code == 200
    assert 'stats' in response.get_json()

# --- TOPICS ---

def test_create_topic(client, admin_headers):
    response = client.post('/api/admin/topics', json={"name": "Эндшпиль"}, headers=admin_headers)
    assert response.status_code == 201
    assert response.get_json()['topic']['name'] == "Эндшпиль"

def test_update_topic(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "Old"}, headers=admin_headers).get_json()['topic']['id']
    response = client.put(f'/api/admin/topics/{t_id}', json={"name": "New"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.get_json()['topic']['name'] == "New"

def test_delete_topic(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "Del"}, headers=admin_headers).get_json()['topic']['id']
    response = client.delete(f'/api/admin/topics/{t_id}', headers=admin_headers)
    assert response.status_code == 200

# --- LESSONS ---

def test_create_lesson(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "T1"}, headers=admin_headers).get_json()['topic']['id']
    data = {"title": "Мат", "topic_id": t_id, "content": "Текст"}
    response = client.post('/api/admin/lessons', json=data, headers=admin_headers)
    assert response.status_code == 201

def test_update_lesson(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "T2"}, headers=admin_headers).get_json()['topic']['id']
    l_id = client.post('/api/admin/lessons', json={"title": "L", "topic_id": t_id}, headers=admin_headers).get_json()['lesson']['id']
    response = client.put(f'/api/admin/lessons/{l_id}', json={"title": "Updated L"}, headers=admin_headers)
    assert response.status_code == 200

def test_delete_lesson(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "T3"}, headers=admin_headers).get_json()['topic']['id']
    l_id = client.post('/api/admin/lessons', json={"title": "Del L", "topic_id": t_id}, headers=admin_headers).get_json()['lesson']['id']
    response = client.delete(f'/api/admin/lessons/{l_id}', headers=admin_headers)
    assert response.status_code == 200

# --- EXERCISES ---

def test_create_exercise(client, admin_headers):
    t_id = client.post('/api/admin/topics', json={"name": "T4"}, headers=admin_headers).get_json()['topic']['id']
    l_id = client.post('/api/admin/lessons', json={"title": "L4", "topic_id": t_id}, headers=admin_headers).get_json()['lesson']['id']
    data = {"lesson_id": l_id, "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "correct_move": "e4"}
    response = client.post('/api/admin/exercises', json=data, headers=admin_headers)
    assert response.status_code == 201

# --- TESTS & QUESTIONS ---

def test_create_test_with_questions(client, admin_headers):
    data = {"title": "Итоговый", "questions": []}
    response = client.post('/api/admin/tests', json=data, headers=admin_headers)
    assert response.status_code == 201

def test_add_question_to_test(client, admin_headers):
    test_id = client.post('/api/admin/tests', json={"title": "Q Test"}, headers=admin_headers).get_json()['test']['id']
    data = {
        "question_text": "Как ходит конь?", 
        "correct_answer": "Буквой Г",
        "options": ["Прямо", "Буквой Г"]
    }
    response = client.post(f'/api/admin/tests/{test_id}/questions', json=data, headers=admin_headers)
    assert response.status_code == 201
    assert response.get_json()['question']['question_text'] == "Как ходит конь?"

# --- STATS ---

def test_get_platform_stats(client, admin_headers):
    response = client.get('/api/admin/stats', headers=admin_headers)
    assert response.status_code == 200
    assert 'total_games' in response.get_json()