import pytest
from app.models.user import User
from app.models.game import Game
from flask_jwt_extended import create_access_token

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        user = User(username="testuser", email="test@test.com")
        user.set_password("password123")
        user.elo_rating = 1200
        from app import db
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

def test_create_game_ai(client, auth_headers):
    data = {"mode": "ai", "color": "white", "bot_level": 5}
    response = client.post('/api/games/', json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['game']['mode'] == 'ai'

def test_make_valid_move(client, auth_headers):
    game_res = client.post('/api/games/', json={"mode": "ai", "color": "white"}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    
    move_data = {"move": "e2e4"}
    response = client.post(f'/api/games/{game_id}/move', json=move_data, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['move']['notation'] == 'e4'
    assert 'ai_move' in response.json

def test_make_invalid_move(client, auth_headers):
    game_res = client.post('/api/games/', json={"mode": "ai"}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    
    response = client.post(f'/api/games/{game_id}/move', json={"move": "e2e5"}, headers=auth_headers)
    assert response.status_code == 400
    assert "error" in response.json

def test_resign_and_elo_update(client, auth_headers, app):
    game_res = client.post('/api/games/', json={"mode": "ai", "bot_level": 10}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    
    response = client.post(f'/api/games/{game_id}/resign', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['game']['status'] == 'finished'
    
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user.elo_rating != 1200

def test_get_history(client, auth_headers):
    client.post('/api/games/', json={"mode": "ai"}, headers=auth_headers)
    response = client.get('/api/games/history', headers=auth_headers)
    assert response.status_code == 200
    assert 'games' in response.json

def test_export_pgn_after_moves(client, auth_headers):
    game_res = client.post('/api/games/', json={"mode": "ai"}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    
    client.post(f'/api/games/{game_id}/move', json={"move": "e2e4"}, headers=auth_headers)
    client.post(f'/api/games/{game_id}/resign', headers=auth_headers)
    
    response = client.get(f'/api/games/{game_id}/pgn', headers=auth_headers)
    assert response.status_code == 200
    assert "pgn" in response.json
    assert "e4" in response.json['pgn']

def test_get_game_moves(client, auth_headers):
    game_res = client.post('/api/games/', json={"mode": "ai"}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    client.post(f'/api/games/{game_id}/move', json={"move": "d2d4"}, headers=auth_headers)
    
    response = client.get(f'/api/games/{game_id}/moves', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json['moves']) >= 2

def test_move_format_validation(client, auth_headers):
    game_res = client.post('/api/games/', json={"mode": "ai"}, headers=auth_headers)
    game_id = game_res.json['game']['id']
    
    response = client.post(f'/api/games/{game_id}/move', json={"move": "e2"}, headers=auth_headers)
    assert response.status_code == 400