import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.user import User
from app.models.game import Game
from app.models.mistake import Mistake
from app.models.chat import ChatSession, ChatMessage
from flask_jwt_extended import create_access_token

class ChatTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            username='darya_pro', 
            elo_rating=1600, 
            level='advanced',
            weak_topics=['opening', 'fork']
        )
        self.user.set_password('secure_pass')
        db.session.add(self.user)
        
        game = Game(white_id=1, pgn="1. e4 e5 2. Nf3 Nc6", status='finished')
        mistake = Mistake(user_id=1, category='tactic', explanation='Зевок ферзя')
        db.session.add_all([game, mistake])
        db.session.commit()
        
        self.token = create_access_token(identity=str(self.user.id))
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_context_building(self):
        """Проверяем, что сервис правильно собирает данные из БД в текст"""
        from app.services.chat_service import ChatService
        context = ChatService.get_user_chess_context(self.user.id)
        
        self.assertIn("1600", context)
        self.assertIn("advanced", context)
        self.assertIn("Зевок ферзя", context)
        self.assertIn("1. e4 e5", context)


    @patch('app.services.chat_service.client.chat.completions.create')
    def test_send_message_api(self, mock_openai):
        mock_choice = MagicMock()
        mock_choice.message.content = "Хороший вопрос! Тебе стоит подтянуть дебюты."
        mock_openai.return_value.choices = [mock_choice]

        session_res = self.client.post('/api/chat/sessions', headers=self.headers)
        session_id = session_res.get_json()['session_id']

        res = self.client.post(
            f'/api/chat/sessions/{session_id}/send',
            headers=self.headers,
            json={'message': 'Над чем мне работать?'}
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("Хороший вопрос", res.get_json()['assistant_response'])
        
        messages_count = ChatMessage.query.filter_by(session_id=session_id).count()
        self.assertEqual(messages_count, 2)
