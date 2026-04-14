import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from app.models.user import User
from app.models.game import Game
from app.models.mistake import Mistake

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if os.environ.get("OPENAI_API_KEY") else None

class ChatService:
    @staticmethod
    def _extract_game_reference(user_message):
        """
        Supports prompts like:
        - "разбери партию #2"
        - "проанализируй мою игру 5"
        Returns integer game id or None.
        """
        if not user_message:
            return None
        msg = str(user_message)
        match = re.search(r'#\s*(\d+)', msg)
        if match:
            return int(match.group(1))
        match = re.search(r'парт(ия|ию|ии)\s*(?:№|#)?\s*(\d+)', msg.lower())
        if match:
            return int(match.group(2))
        return None

    @staticmethod
    def _detect_model_needed(user_message):
        """
        ИНТЕЛЛЕКТУАЛЬНЫЙ МАРШРУТИЗАТОР:
        Анализирует текст и выбирает gpt-4o для сложных задач 
        и gpt-4o-mini для простых вопросов.
        """
        msg = user_message.lower()
        
        # Список триггеров для глубокого анализа
        complex_triggers = [
            'почему', 'проанализируй', 'ошибка', 'pgn', 'разбери', 
            'тактика', 'стратегия', 'план', 'дебют', 'эндшпиль'
        ]
        
        # Если есть шахматная нотация (например, 1. e4) или ключевые слова
        if '1.' in msg or any(word in msg for word in complex_triggers):
            return "gpt-4o"
            
        return "gpt-4o-mini"

    @staticmethod
    def get_user_chess_context(user_id, user_message=None):
        user = User.query.get(user_id)
        if not user:
            return "Данные игрока недоступны."

        context = f"Ученик: {user.username}. Уровень: {user.level}. Рейтинг ELO: {user.elo_rating}.\n"
        
        if user.weak_topics and isinstance(user.weak_topics, list):
            context += f"Темы, требующие внимания: {', '.join(map(str, user.weak_topics))}.\n"

        recent_mistakes = Mistake.query.filter_by(user_id=user_id).order_by(Mistake.created_at.desc()).limit(3).all()
        if recent_mistakes:
            context += "\nПоследние тактические промахи ученика:\n"
            for m in recent_mistakes:
                context += f"- [{m.category}] {m.explanation} (Потеря оценки: {m.evaluation_loss})\n"

        recent_games = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).order_by(Game.created_at.desc()).limit(5).all()

        if recent_games:
            context += "\nПоследние партии ученика:\n"
            for g in recent_games:
                context += f"- Игра #{g.id}: статус={g.status}, результат={g.result or 'в процессе'}, дата={g.created_at.strftime('%Y-%m-%d')}\n"

        requested_game_id = ChatService._extract_game_reference(user_message)
        target_game = None
        if requested_game_id:
            target_game = Game.query.filter(
                Game.id == requested_game_id,
                ((Game.white_id == user_id) | (Game.black_id == user_id))
            ).first()
            if target_game:
                context += f"\nПользователь явно запросил партию #{requested_game_id}.\n"
            else:
                context += (
                    f"\nПользователь запросил партию #{requested_game_id}, но у него нет такой партии. "
                    "Нужно использовать последнюю доступную партию пользователя для анализа.\n"
                )

        if not target_game and recent_games:
            target_game = recent_games[0]

        if target_game and target_game.pgn:
            context += f"\nКонтекст партии для анализа (id={target_game.id}, PGN):\n{target_game.pgn}\n"
        elif target_game:
            context += f"\nПартия id={target_game.id} найдена, но PGN пока отсутствует.\n"

        return context

    @staticmethod
    def get_ai_response(user_id, user_message):
        # 1. АВТОМАТИЧЕСКИЙ ВЫБОР МОДЕЛИ
        model = ChatService._detect_model_needed(user_message)
        
        chess_context = ChatService.get_user_chess_context(user_id, user_message=user_message)
        system_instruction = ChatService._get_system_instruction(chess_context)

        print(f"--- ROUTING: Используется {model} для вопроса: {user_message[:30]}... ---")

        try:
            if client is None:
                return "ИИ-сервис временно недоступен: не настроен OPENAI_API_KEY."
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Извини, я временно недоступен: {str(e)}"

    @staticmethod
    def get_ai_response_stream(user_id, user_message):
        # 1. АВТОМАТИЧЕСКИЙ ВЫБОР МОДЕЛИ ДЛЯ СТРИМА
        model = ChatService._detect_model_needed(user_message)
        
        chess_context = ChatService.get_user_chess_context(user_id, user_message=user_message)
        system_instruction = ChatService._get_system_instruction(chess_context)

        print(f"--- STREAM ROUTING: Используется {model} ---")

        try:
            if client is None:
                yield "ИИ-сервис временно недоступен: не настроен OPENAI_API_KEY."
                return
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                stream=True 
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"Ошибка стриминга: {str(e)}"

    @staticmethod
    def _get_system_instruction(chess_context):
        return f"""
        Ты — добрый и профессиональный шахматный тренер для детей и подростков. 
        Твоя задача: отвечать на вопросы, анализировать партии и давать советы по обучению.
        
        ВОТ ТВОИ ЗНАНИЯ ОБ УЧЕНИКЕ:
        {chess_context}
        
        ИНСТРУКЦИИ:
        1. Если ученик спрашивает "Как я играю?", используй данные об ошибках и ELO.
        2. Если в контексте есть блок "Контекст партии для анализа (id=..., PGN)", ОБЯЗАТЕЛЬНО анализируй именно эту партию.
        3. НИКОГДА не проси пользователя прислать PGN, если в контексте уже есть PGN.
        4. Если пользователь просит партию #N, а в контексте указано, что такой партии нет, анализируй последнюю доступную партию из контекста и явно скажи, какую партию ты анализируешь.
        3. Отвечай на русском языке, поддерживай ученика, используй шахматные термины.
        5. Не пиши слишком длинные тексты.
        """