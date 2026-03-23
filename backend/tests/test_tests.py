import pytest
from app.models.test import Test as ChessTest
from app.models.test_question import TestQuestion
from app.models.topic import Topic
from app import db
from seed import run_seed

@pytest.fixture(autouse=True)
def setup_test_data(app):
    with app.app_context():
        run_seed(app)
        
        if ChessTest.query.count() == 0:
            topic = Topic.query.get(1) or Topic(name="Основы", order=1)
            if not topic.id: 
                db.session.add(topic)
                db.session.commit()
            
            test = ChessTest(id=1, title="Определение уровня", topic_id=topic.id)
            db.session.add(test)
            db.session.commit()
            
            for i in range(1, 11):
                q = TestQuestion(
                    id=i, test_id=1, question_text=f"Вопрос {i}",
                    correct_answer="e4", options=["e4", "d4"], order=i
                )
                db.session.add(q)
            db.session.commit()
        else:
            t = ChessTest.query.get(1)
            if t:
                t.topic_id = 1
                db.session.commit()

@pytest.fixture
def auth_headers(client):
    login_res = client.post('/api/auth/login', json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    token = login_res.json.get('access_token')
    return {'Authorization': f'Bearer {token}'}

def test_get_tests_list(client, auth_headers):
    res = client.get('/api/tests/', headers=auth_headers)
    assert res.status_code == 200
    assert 'tests' in res.json
    assert len(res.json['tests']) > 0

def test_get_single_test_detail(client, auth_headers):
    res = client.get('/api/tests/1', headers=auth_headers)
    assert res.status_code == 200
    assert 'questions' in res.json

def test_start_test_session(client, auth_headers):
    res = client.post('/api/tests/1/start', headers=auth_headers)
    assert res.status_code == 201
    assert 'attempt' in res.json

def test_submit_test_advanced(client, auth_headers):
    client.post('/api/tests/1/start', headers=auth_headers)
    answers = {str(i): "e4" for i in range(1, 11)}
    res = client.post('/api/tests/1/submit', json={"answers": answers}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json['level'] == 'advanced'
    assert res.json['percent'] == 100

def test_weak_topics_detection(client, auth_headers):
    client.post('/api/tests/1/start', headers=auth_headers)
    res = client.post('/api/tests/1/submit', json={"answers": {"1": "wrong"}}, headers=auth_headers)
    assert res.status_code == 200
    assert 1 in res.json['weak_topics']

def test_get_level_summary(client, auth_headers):
    client.post('/api/tests/1/start', headers=auth_headers)
    client.post('/api/tests/1/submit', json={"answers": {"1": "x"}}, headers=auth_headers)
    
    res = client.get('/api/tests/level', headers=auth_headers)
    assert res.status_code == 200
    assert 'level' in res.json
    assert 'weak_topics' in res.json

def test_get_attempts_history(client, auth_headers):
    res = client.get('/api/tests/attempts', headers=auth_headers)
    assert res.status_code == 200
    assert 'attempts' in res.json

def test_submit_without_start_fails(client, auth_headers):
    res = client.post('/api/tests/999/submit', json={"answers": {}}, headers=auth_headers)
    assert res.status_code == 404