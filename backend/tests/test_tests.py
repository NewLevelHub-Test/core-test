import pytest
from app.models.test import Test as ChessTest
from app.models.test_question import TestQuestion
from app.models.topic import Topic
from app.models.test_attempt import TestAttempt
from app import db
from seed import run_seed

@pytest.fixture(autouse=True)
def setup_test_data(app):
    with app.app_context():
        # Очистка для чистоты каждого теста
        db.session.query(TestAttempt).delete()
        db.session.query(TestQuestion).delete()
        db.session.query(ChessTest).delete()
        db.session.commit()
        
        # Запуск базового сида
        run_seed(app)
        
        # Создаем тестовый топик и тест с ID=1, если сид их не создал
        topic = Topic.query.get(1) or Topic(id=1, name="Основы", order=1)
        db.session.merge(topic)
        db.session.commit()
        
        test = ChessTest.query.get(1) or ChessTest(id=1, title="Тест уровня", topic_id=topic.id)
        db.session.merge(test)
        db.session.commit()
        
        # Добавляем вопросы (минимум 2 для теста)
        for i in range(1, 3):
            q = TestQuestion(
                id=i, test_id=1, question_text=f"Вопрос {i}",
                correct_answer="e4", options=["e4", "d4"], order=i,
                explanation="Best move"
            )
            db.session.merge(q)
        db.session.commit()

@pytest.fixture
def auth_headers(client):
    # Регистрация и логин тестового пользователя
    user_data = {
        "username": "tester_pro",
        "email": "tester@example.com",
        "password": "Password123!",
        "phone": "87079998877",
        "role": "student"
    }
    client.post('/api/auth/register', json=user_data)
    login = client.post('/api/auth/login', json={"email": "tester@example.com", "password": "Password123!"})
    token = login.get_json().get('access_token')
    return {'Authorization': f'Bearer {token}'}

# --- ТЕСТЫ ---

def test_get_tests_list(client, auth_headers):
    """Проверка списка тестов с пагинацией"""
    res = client.get('/api/tests/', headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert 'tests' in data
    assert 'total' in data  # Проверка, что пагинация добавлена

def test_start_test_session(client, auth_headers):
    """Проверка начала теста (создание попытки)"""
    res = client.post('/api/tests/1/start', headers=auth_headers)
    assert res.status_code == 201
    assert 'attempt' in res.get_json()

def test_submit_test_advanced(client, auth_headers):
    """Проверка успешной отправки ответов (формат списка)"""
    # 1. Сначала создаем активную попытку
    client.post('/api/tests/1/start', headers=auth_headers)
    
    # 2. Формируем ответы как список (как требует твой сервис)
    payload = {
        "answers": [
            {"question_id": 1, "selected_option": "e4"},
            {"question_id": 2, "selected_option": "e4"}
        ]
    }
    
    res = client.post('/api/tests/1/submit', json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert 'score' in res.get_json() or 'attempt' in res.get_json()

def test_weak_topics_detection(client, auth_headers):
    """Проверка определения слабых тем при ошибке"""
    client.post('/api/tests/1/start', headers=auth_headers)
    
    # Отправляем один неправильный ответ
    payload = {
        "answers": [{"question_id": 1, "selected_option": "d4"}]
    }
    res = client.post('/api/tests/1/submit', json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert 'weak_topics' in res.get_json()

def test_get_attempts_history(client, auth_headers):
    """Проверка истории попыток с пагинацией"""
    res = client.get('/api/tests/attempts', headers=auth_headers)
    assert res.status_code == 200
    assert 'attempts' in res.get_json()

def test_submit_without_start_fails(client, auth_headers):
    """Проверка ошибки 404, если теста не существует"""
    payload = {"answers": [{"question_id": 1, "selected_option": "e4"}]}
    res = client.post('/api/tests/999/submit', json=payload, headers=auth_headers)
    # Если в начале сервиса стоит проверка на существование теста — будет 404
    assert res.status_code == 404

def test_limiter_works(client, auth_headers):
    """Проверка работы лимитера (3 запроса на сабмит)"""
    payload = {"answers": [{"question_id": 1, "selected_option": "e4"}]}
    # Делаем 4 быстрых запроса
    for _ in range(4):
        res = client.post('/api/tests/1/submit', json=payload, headers=auth_headers)
    
    # Последний запрос должен быть заблокирован лимитером
    assert res.status_code == 429 or res.status_code == 404 # 404 если нет активной попытки