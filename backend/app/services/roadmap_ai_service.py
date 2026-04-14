import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            _client = OpenAI(api_key=key)
    return _client


CHESS_CURRICULUM = {
    'beginner': [
        {'topic': 'Шахматная доска и фигуры', 'desc': 'Знакомство с доской, полями и всеми фигурами'},
        {'topic': 'Как ходят фигуры', 'desc': 'Правила ходов пешки, ладьи, слона, коня, ферзя и короля'},
        {'topic': 'Ценность фигур', 'desc': 'Относительная ценность фигур и принципы размена'},
        {'topic': 'Шах, мат и пат', 'desc': 'Понятия шаха, мата и пата. Простейшие маты'},
        {'topic': 'Рокировка и спецходы', 'desc': 'Рокировка, взятие на проходе, превращение пешки'},
        {'topic': 'Основы дебюта', 'desc': 'Принципы начала партии: центр, развитие, безопасность короля'},
        {'topic': 'Тактика: вилка и связка', 'desc': 'Двойной удар (вилка), связка фигур'},
        {'topic': 'Тактика: открытое нападение', 'desc': 'Открытый шах, открытое нападение, рентген'},
        {'topic': 'Простые комбинации', 'desc': 'Комбинации из 2-3 ходов, жертвы для мата'},
        {'topic': 'Основы эндшпиля', 'desc': 'Мат королём и ферзём, королём и ладьёй'},
        {'topic': 'Пешечные окончания', 'desc': 'Правило квадрата, оппозиция, проходная пешка'},
        {'topic': 'Итоговое повторение', 'desc': 'Повторение всех тем, подготовка к соревнованиям'},
    ],
    'intermediate': [
        {'topic': 'Дебютные принципы', 'desc': 'Углубленное изучение дебютных принципов и типичных ошибок'},
        {'topic': 'Итальянская партия', 'desc': 'Итальянская партия и гамбит Эванса'},
        {'topic': 'Сицилианская защита', 'desc': 'Основные варианты сицилианской защиты'},
        {'topic': 'Углубленная тактика', 'desc': 'Вилки, связки, двойные удары, отвлечение'},
        {'topic': 'Комбинационное зрение', 'desc': 'Развитие комбинационного зрения, сложные задачи'},
        {'topic': 'Пешечная структура', 'desc': 'Типы пешечных структур и планы игры'},
        {'topic': 'Атака на короля', 'desc': 'Принципы атаки, типичные жертвы'},
        {'topic': 'Защита и контратака', 'desc': 'Методы защиты, профилактика, контратака'},
        {'topic': 'Ладейные окончания', 'desc': 'Позиция Лусены, позиция Филидора'},
        {'topic': 'Лёгкофигурные окончания', 'desc': 'Слон vs конь, хороший vs плохой слон'},
        {'topic': 'Позиционная игра', 'desc': 'Слабые поля, открытые линии, форпосты'},
        {'topic': 'Турнирная практика', 'desc': 'Применение всех концепций на практике'},
    ],
    'advanced': [
        {'topic': 'Дебютный репертуар', 'desc': 'Построение репертуара за белых и за чёрных'},
        {'topic': 'Испанская партия', 'desc': 'Глубокое изучение испанской партии'},
        {'topic': 'Защита Нимцовича', 'desc': 'Стратегические идеи защиты Нимцовича'},
        {'topic': 'Сложная тактика', 'desc': 'Многоходовые комбинации, промежуточные ходы'},
        {'topic': 'Планы миттельшпиля', 'desc': 'Типичные планы в различных структурах'},
        {'topic': 'Динамика и статика', 'desc': 'Динамическое и статическое преимущество'},
        {'topic': 'Жертва качества', 'desc': 'Позиционная и тактическая жертва качества'},
        {'topic': 'Техника реализации', 'desc': 'Реализация материального и позиционного перевеса'},
        {'topic': 'Сложные окончания', 'desc': 'Ферзевые и ладейные окончания с пешками'},
        {'topic': 'Анализ партий', 'desc': 'Методика анализа собственных партий'},
        {'topic': 'Психология шахмат', 'desc': 'Управление временем, подготовка к турнирам'},
        {'topic': 'Мастер-план', 'desc': 'Долгосрочный план совершенствования'},
    ],
}

WEEK_TASK_TEMPLATE = [
    {'day': 1, 'type': 'lesson',   'suffix': 'Теория и основы'},
    {'day': 2, 'type': 'exercise', 'suffix': 'Практические задания'},
    {'day': 3, 'type': 'lesson',   'suffix': 'Углубленное изучение'},
    {'day': 4, 'type': 'exercise', 'suffix': 'Решение задач'},
    {'day': 5, 'type': 'test',     'suffix': 'Контрольный тест'},
]


def get_curriculum(level):
    return CHESS_CURRICULUM.get(level, CHESS_CURRICULUM['beginner'])


def generate_task_content(topic_name, task_title, task_type, level, week_description=''):
    client = _get_client()
    if not client:
        return _fallback_content(topic_name, task_title, task_type)

    level_labels = {
        'beginner': 'начинающего (5-12 лет)',
        'intermediate': 'среднего уровня (8-14 лет)',
        'advanced': 'продвинутого (10-16 лет)',
    }
    level_label = level_labels.get(level, level_labels['beginner'])

    if task_type == 'test':
        return _generate_test_content(client, topic_name, level_label)

    prompt = f"""Ты — профессиональный шахматный тренер. Создай урок для ученика {level_label}.

Тема недели: {topic_name}
Название урока: {task_title}
Тип: {'Теоретический урок' if task_type == 'lesson' else 'Практические упражнения'}

Верни JSON (и ТОЛЬКО JSON, без markdown-обёрток):
{{
  "steps": [
    {{
      "title": "Заголовок шага",
      "content": "Подробное объяснение на 3-5 предложений. Используй шахматные примеры.",
      "tip": "Полезный совет или интересный факт"
    }}
  ],
  "quiz": [
    {{
      "question": "Текст вопроса",
      "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
      "correct": 0,
      "explanation": "Почему этот ответ правильный"
    }}
  ]
}}

Требования:
- 3-4 шага урока, каждый с понятным объяснением
- 3 вопроса теста, множественный выбор из 4 вариантов
- correct — индекс правильного ответа (0-3)
- Контент на русском языке, доступный для детей
- Используй шахматную терминологию, подходящую для уровня
- Для упражнений добавь конкретные позиции и ходы в описании"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты шахматный тренер. Отвечай ТОЛЬКО валидным JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        steps = data.get('steps', [])
        quiz = data.get('quiz', [])
        if not steps or not quiz:
            return _fallback_content(topic_name, task_title, task_type)
        return {'steps': steps, 'quiz': quiz}
    except Exception as e:
        logger.error(f"OpenAI content generation failed: {e}")
        return _fallback_content(topic_name, task_title, task_type)


def _generate_test_content(client, topic_name, level_label):
    prompt = f"""Ты — шахматный тренер. Создай контрольный тест по теме "{topic_name}" для ученика {level_label}.

Верни JSON (и ТОЛЬКО JSON):
{{
  "steps": [
    {{
      "title": "Контрольный тест",
      "content": "Сейчас проверим, как ты усвоил тему «{topic_name}». Ответь на 5 вопросов.",
      "tip": "Не торопись, внимательно читай каждый вопрос!"
    }}
  ],
  "quiz": [
    {{
      "question": "Текст вопроса",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Объяснение"
    }}
  ]
}}

Требования:
- 1 шаг (введение в тест)
- 5 вопросов теста по теме
- correct — индекс правильного ответа (0-3)
- Вопросы на русском, доступные для детей"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты шахматный тренер. Отвечай ТОЛЬКО валидным JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return {'steps': data.get('steps', []), 'quiz': data.get('quiz', [])}
    except Exception as e:
        logger.error(f"OpenAI test generation failed: {e}")
        return _fallback_content(topic_name, "Контрольный тест", 'test')


def _fallback_content(topic_name, task_title, task_type):
    return {
        'steps': [
            {
                'title': task_title,
                'content': f'Сегодня мы изучаем тему: {topic_name}. '
                           f'Это важная тема в шахматах, которая поможет тебе стать сильнее.',
                'tip': 'Старайся запомнить ключевые идеи!',
            },
            {
                'title': 'Ключевые моменты',
                'content': f'В теме «{topic_name}» важно понимать основные принципы и уметь применять их на практике. '
                           f'Попробуй разобрать несколько примеров самостоятельно.',
                'tip': 'Практика — лучший способ научиться!',
            },
        ],
        'quiz': [
            {
                'question': f'Что является главной целью изучения темы «{topic_name}»?',
                'options': [
                    'Улучшить понимание игры',
                    'Выучить все дебюты наизусть',
                    'Играть только быстрые партии',
                    'Не думать во время игры',
                ],
                'correct': 0,
                'explanation': 'Каждая тема помогает глубже понять игру и стать сильнее.',
            },
            {
                'question': 'Какой лучший способ закрепить новые знания в шахматах?',
                'options': [
                    'Только читать книги',
                    'Практиковаться и решать задачи',
                    'Смотреть видео без анализа',
                    'Играть без анализа ошибок',
                ],
                'correct': 1,
                'explanation': 'Практика и решение задач — лучший способ закрепить знания.',
            },
            {
                'question': 'Что важно делать после каждой сыгранной партии?',
                'options': [
                    'Сразу начать новую партию',
                    'Забыть о ней',
                    'Проанализировать свои ходы',
                    'Поменять дебют',
                ],
                'correct': 2,
                'explanation': 'Анализ партии помогает найти ошибки и улучшить игру.',
            },
        ],
    }
