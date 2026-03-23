import pytest
from app.models.user import User
from app.models.topic import Topic
from app.models.roadmap import Roadmap
from app.models.roadmap_week import RoadmapWeek
from app.models.daily_task import DailyTask
from flask_jwt_extended import create_access_token
from app import db

@pytest.fixture
def auth_setup(app):
    with app.app_context():
        user = User(username="student_chess", email="student@test.com", level="beginner")
        user.set_password("password123")
        db.session.add(user)
        
        topic = Topic(name="Основы", description="Начало пути", order=1)
        db.session.add(topic)
        db.session.commit()
        
        token = create_access_token(identity=str(user.id))
        return {
            'headers': {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            'user_id': user.id
        }

def test_generate_roadmap_success(client, auth_setup):
    data = {"level": "beginner"}
    response = client.post('/api/roadmap/generate', json=data, headers=auth_setup['headers'])
    
    assert response.status_code == 201
    assert 'roadmap' in response.json
    assert len(response.json['weeks']) > 0

def test_generate_roadmap_invalid_level(client, auth_setup):
    data = {"level": "pro_player"}
    response = client.post('/api/roadmap/generate', json=data, headers=auth_setup['headers'])
    assert response.status_code == 400

def test_get_roadmap_exists(client, auth_setup):
    client.post('/api/roadmap/generate', json={"level": "beginner"}, headers=auth_setup['headers'])
    response = client.get('/api/roadmap/', headers=auth_setup['headers'])
    assert response.status_code == 200
    assert 'weeks' in response.json

def test_complete_daily_task(client, auth_setup):
    gen_res = client.post('/api/roadmap/generate', json={"level": "beginner"}, headers=auth_setup['headers'])
    task_id = gen_res.json['weeks'][0]['daily_tasks'][0]['id']
    
    response = client.post(f'/api/roadmap/tasks/{task_id}/complete', headers=auth_setup['headers'])
    assert response.status_code == 200
    assert response.json['task']['is_completed'] is True

def test_complete_week_manual(client, auth_setup):
    gen_res = client.post('/api/roadmap/generate', json={"level": "beginner"}, headers=auth_setup['headers'])
    week_id = gen_res.json['weeks'][0]['id']
    
    response = client.post(f'/api/roadmap/weeks/{week_id}/complete', headers=auth_setup['headers'])
    assert response.status_code == 200
    assert response.json['week']['is_completed'] is True

def test_get_progress_data(client, auth_setup):
    gen_res = client.post('/api/roadmap/generate', json={"level": "beginner"}, headers=auth_setup['headers'])
    task_id = gen_res.json['weeks'][0]['daily_tasks'][0]['id']
    client.post(f'/api/roadmap/tasks/{task_id}/complete', headers=auth_setup['headers'])
    
    response = client.get('/api/roadmap/progress', headers=auth_setup['headers'])
    assert response.status_code == 200
    assert response.json['completed_tasks'] == 1
    assert response.json['progress_percent'] > 0

def test_roadmap_not_found_error(client, auth_setup):
    response = client.get('/api/roadmap/', headers=auth_setup['headers'])
    assert response.status_code == 404

def test_get_week_detail(client, auth_setup):
    gen_res = client.post('/api/roadmap/generate', json={"level": "beginner"}, headers=auth_setup['headers'])
    week_id = gen_res.json['weeks'][0]['id']
    
    response = client.get(f'/api/roadmap/weeks/{week_id}', headers=auth_setup['headers'])
    assert response.status_code == 200
    assert response.json['week']['id'] == week_id