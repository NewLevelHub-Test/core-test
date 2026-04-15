# План внедрения ИИ-тренера (ChatGPT-бот)

> Персональный шахматный ИИ-тренер с доступом к профилю, истории игр, анализу ошибок и проверке партий через PGN.

---

## Оглавление

1. [Общая архитектура](#1-общая-архитектура)
2. [Контекст данных для бота](#2-контекст-данных-для-бота)
3. [Этапы для бэкендера](#3-этапы-для-бэкендера)
4. [Этапы для фронтендера](#4-этапы-для-фронтендера)
5. [Промпт-инжиниринг](#5-промпт-инжиниринг)
6. [Безопасность и лимиты](#6-безопасность-и-лимиты)
7. [Оценка сроков](#7-оценка-сроков)

---

## 1. Общая архитектура

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│   Frontend   │◄─────►│   Flask Backend   │◄─────►│  PostgreSQL  │
│  (chat UI)   │  JWT  │  /api/chat/*      │       │  (users,     │
│              │       │                    │       │   games,     │
└──────────────┘       │  ChatService       │       │   moves,     │
                       │    ▼               │       │   mistakes,  │
                       │  Сборщик контекста │       │   chat_msgs) │
                       │    ▼               │       └──────────────┘
                       │  OpenAI API        │
                       │  (gpt-4o / gpt-4o-mini)   │
                       └──────────────────┘
```

**Принцип:** Фронтенд НЕ общается с OpenAI напрямую. Все запросы идут через наш бэкенд, который:
1. Собирает контекст пользователя (профиль, статистика, ошибки, партии)
2. Формирует system prompt с этим контекстом
3. Отправляет в OpenAI API
4. Возвращает ответ клиенту

Это критически важно для безопасности (API-ключ на сервере) и контроля расходов.

---

## 2. Контекст данных для бота

Бот получает доступ к данным через **внутренние сервисы**, а не через API-запросы. Какие данные собираем для каждого запроса:

### Всегда в system prompt (лёгкие данные):
| Источник | Что берём | Откуда |
|----------|-----------|--------|
| `User` | username, level, elo_rating, weak_topics | `UserService.get_profile()` |
| `User stats` | total_games, wins, losses, lessons_completed | `UserService.get_stats()` |
| `Progress` | пройденные темы и уроки | `Progress` модель |

### По запросу (тяжёлые данные, подгружаем при необходимости):
| Источник | Что берём | Когда подгружаем |
|----------|-----------|-----------------|
| `Game` + `Move` | PGN конкретной партии, ходы с оценками | Когда пользователь спрашивает о конкретной игре |
| `Mistake` | ошибки пользователя, категории, потеря оценки | Когда бот анализирует слабые стороны |
| `TestAttempt` | результаты тестов, неправильные ответы | Когда обсуждаем прогресс в обучении |
| `Roadmap` | текущий план обучения, прогресс по неделям | Когда обсуждаем план тренировок |
| PGN-парсинг | Внешний PGN (вставленный пользователем) | Когда пользователь просит проверить партию |

### Проверка партий через PGN:
- Пользователь вставляет PGN в чат
- Бэкенд парсит PGN через `python-chess`
- Прогоняет ключевые позиции через Stockfish (уже есть `ChessService`)
- Находит ошибки/блюндеры (уже есть `AnalysisService`)
- Результат анализа передаётся боту как контекст
- Бот объясняет ошибки человеческим языком

---

## 3. Этапы для бэкендера

### Этап 1: Модель и миграции (1-2 дня)

**Файл:** `backend/app/models/chat.py`

Создать две модели:

```python
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))  # авто-генерация из первого сообщения
    context_type = db.Column(db.String(50))  # 'general', 'game_review', 'training'
    context_data = db.Column(db.JSON)  # {'game_id': 123} или {'topic': 'endgame'}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20))  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer)  # для учёта расхода
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Действия:**
- Добавить модели в `app/models/__init__.py`
- Создать миграцию: `flask db migrate -m "add chat models"`
- Применить: `flask db upgrade`

---

### Этап 2: Сервис контекста (2-3 дня)

**Файл:** `backend/app/services/chat_context_service.py`

Этот сервис собирает контекст пользователя для system prompt:

```python
class ChatContextService:

    @staticmethod
    def build_system_prompt(user_id, context_type=None, context_data=None):
        """Собирает system prompt с данными пользователя."""
        # 1. Базовый профиль (всегда)
        # 2. Статистика (всегда)
        # 3. Слабые темы и частые ошибки (всегда)
        # 4. Контекст конкретной игры (если context_type == 'game_review')
        # 5. Контекст темы обучения (если context_type == 'training')
        pass

    @staticmethod
    def get_user_summary(user_id):
        """Краткая сводка: elo, уровень, слабые стороны."""
        pass

    @staticmethod
    def get_recent_mistakes(user_id, limit=10):
        """Последние ошибки из таблицы mistakes."""
        pass

    @staticmethod
    def get_game_context(game_id):
        """PGN + ходы + оценки для конкретной партии."""
        pass

    @staticmethod
    def parse_external_pgn(pgn_text):
        """Парсит PGN через python-chess, прогоняет через Stockfish."""
        pass
```

**Ключевой момент:** Контекст нужно ограничивать по токенам. GPT-4o поддерживает 128K токенов, но чем больше контекст — тем дороже. Рекомендуется:
- System prompt: до 2000 токенов
- История чата: последние 20 сообщений
- Контекст игры: только ключевые моменты (ошибки, критические позиции)

---

### Этап 3: OpenAI интеграция (2-3 дня)

**Файл:** `backend/app/services/chat_service.py`

```python
import openai
from app.services.chat_context_service import ChatContextService

class ChatService:

    @staticmethod
    def send_message(user_id, session_id, user_message):
        """
        1. Загрузить историю сообщений сессии
        2. Собрать system prompt через ChatContextService
        3. Детектировать PGN в сообщении → если есть, проанализировать
        4. Отправить в OpenAI
        5. Сохранить оба сообщения в БД
        6. Вернуть ответ
        """
        pass

    @staticmethod
    def create_session(user_id, context_type='general', context_data=None):
        pass

    @staticmethod
    def get_sessions(user_id):
        pass

    @staticmethod
    def get_session_messages(session_id, user_id):
        pass
```

**Конфигурация:**

В `app/config.py` добавить:
```python
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')  # дешевле для старта
CHAT_MAX_TOKENS = 1000           # макс. длина ответа
CHAT_MAX_MESSAGES_PER_DAY = 50   # лимит на пользователя
CHAT_MAX_HISTORY = 20            # сколько сообщений хранить в контексте
```

**Выбор модели:**
| Модель | Цена (input/output за 1M токенов) | Рекомендация |
|--------|-----------------------------------|-------------|
| `gpt-4o-mini` | $0.15 / $0.60 | Для старта, быстрый, дешёвый |
| `gpt-4o` | $2.50 / $10.00 | Для глубокого анализа партий |

Рекомендация: начать с `gpt-4o-mini`, для анализа партий можно переключать на `gpt-4o`.

---

### Этап 4: API роуты (1-2 дня)

**Файл:** `backend/app/routes/chat_routes.py`

```
POST   /api/chat/sessions                  — создать новую сессию
GET    /api/chat/sessions                  — список сессий пользователя
GET    /api/chat/sessions/<id>             — получить сессию с сообщениями
POST   /api/chat/sessions/<id>/messages    — отправить сообщение (основной эндпоинт)
DELETE /api/chat/sessions/<id>             — удалить сессию
POST   /api/chat/analyze-pgn              — отправить PGN для анализа + объяснения
POST   /api/chat/quick                    — быстрый вопрос без сессии (для виджета)
```

**Зарегистрировать blueprint в `app/__init__.py`:**
```python
from app.routes.chat_routes import chat_bp
app.register_blueprint(chat_bp, url_prefix='/api/chat')
```

**Rate limiting (уже есть `limiter`):**
```python
@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
@limiter.limit("30/hour")  # 30 сообщений в час на пользователя
def send_message(session_id):
    ...
```

---

### Этап 5: Streaming (опционально, улучшение UX) (2-3 дня)

Для лучшего UX — ответ бота появляется посимвольно (как в ChatGPT):

```python
@chat_bp.route('/sessions/<int:session_id>/stream', methods=['POST'])
@jwt_required()
def stream_message(session_id):
    def generate():
        for chunk in openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            stream=True
        ):
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')
```

**Приоритет:** Можно пропустить на первом этапе и сделать обычный request-response.

---

### Этап 6: Тесты (1-2 дня)

**Файл:** `backend/tests/test_chat.py`

Что тестировать:
- Создание/получение/удаление сессий
- Отправка сообщения и получение ответа (мокаем OpenAI)
- Сборка контекста (проверяем что данные пользователя попадают в prompt)
- Rate limiting (проверяем что после N запросов — 429)
- PGN-парсинг и валидация
- Авторизация (нельзя читать чужие сессии)

---

## 4. Этапы для фронтендера

### Этап 1: Страница чата (2-3 дня)

**Файл:** `frontend/chat.html`

Основной интерфейс чата с ИИ-тренером:

**Структура страницы:**
```
┌────────────────────────────────────────────────┐
│  ← Назад    ИИ Тренер    [Новый чат]          │
├──────────┬─────────────────────────────────────┤
│          │                                     │
│ Сессии   │   Область сообщений                 │
│          │                                     │
│ • Анализ │   🤖 Привет! Я ваш шахматный       │
│   партии │      тренер. Могу помочь с...       │
│          │                                     │
│ • Мои    │   👤 Проанализируй мою последнюю   │
│   ошибки │      партию                         │
│          │                                     │
│ • Как    │   🤖 Я посмотрел вашу партию...     │
│   играть │      На 15-м ходу вы сыграли Nf3,  │
│   эндшп. │      но лучше было Bg5 потому что...│
│          │                                     │
├──────────┴─────────────────────────────────────┤
│  [📎 PGN] Введите сообщение...        [➤]     │
└────────────────────────────────────────────────┘
```

**Компоненты:**
1. **Sidebar:** список сессий чата (GET `/api/chat/sessions`)
2. **Chat area:** сообщения текущей сессии, скролл вниз при новом сообщении
3. **Input area:** текстовое поле + кнопка отправки + кнопка вставки PGN
4. **Quick actions:** кнопки-подсказки для частых запросов

---

### Этап 2: API-функции (1 день)

**Файл:** `frontend/api.js` — добавить функции:

```javascript
// Сессии
async function getChatSessions() { ... }
async function createChatSession(contextType, contextData) { ... }
async function deleteChatSession(sessionId) { ... }

// Сообщения
async function sendChatMessage(sessionId, message) { ... }
async function getChatMessages(sessionId) { ... }

// Быстрые действия
async function analyzeGameWithAI(gameId) { ... }
async function quickAIQuestion(question) { ... }
```

---

### Этап 3: Markdown-рендеринг сообщений (1-2 дня)

Бот будет отвечать с markdown (жирный текст, списки, шахматная нотация). Нужно:

1. Подключить **marked.js** (CDN) для рендеринга markdown → HTML
2. Стилизовать сообщения бота и пользователя по-разному
3. Подсветить шахматную нотацию (ходы вроде `Nf3`, `e4`, `O-O`)
4. Добавить кнопку «копировать» для PGN-фрагментов в ответах

---

### Этап 4: Быстрые действия / контекстные кнопки (1-2 дня)

На первом сообщении (пустой чат) показываем кнопки-подсказки:

```
┌───────────────────────┐  ┌───────────────────────┐
│ 📊 Анализ последней   │  │ 🔍 Мои слабые стороны │
│    партии             │  │                       │
└───────────────────────┘  └───────────────────────┘
┌───────────────────────┐  ┌───────────────────────┐
│ 📋 Проверить PGN      │  │ 📚 Что мне изучать    │
│    партию             │  │    дальше?            │
└───────────────────────┘  └───────────────────────┘
```

При нажатии — автоматически отправляется соответствующий запрос.

---

### Этап 5: Интеграция в существующие страницы (2-3 дня)

Добавить кнопку/виджет вызова ИИ-тренера на ключевых страницах:

| Страница | Интеграция |
|----------|-----------|
| `hist.html` (история) | Кнопка «Спросить ИИ» рядом с каждой партией → открывает чат с контекстом этой игры |
| `analysis.html` (анализ) | Кнопка «Объяснить» рядом с найденными ошибками → бот объясняет почему ход плохой |
| `Dashboard.html` | Мини-виджет «Совет дня» от ИИ на основе статистики |
| `study.html` (обучение) | Кнопка «Не понимаю, объясни» в каждом уроке → чат с контекстом темы |
| `test_result.html` | Кнопка «Разобрать ошибки» → бот объясняет неправильные ответы |

**Виджет (плавающая кнопка):**

На всех страницах — плавающая кнопка в правом нижнем углу для быстрого доступа к чату:
```html
<div id="ai-chat-widget" class="fixed bottom-6 right-6 z-50">
    <button onclick="openChat()" class="bg-blue-600 text-white rounded-full p-4 shadow-lg">
        🤖
    </button>
</div>
```

---

### Этап 6: Streaming UI (опционально) (1-2 дня)

Если бэкенд реализует SSE streaming:

```javascript
async function streamChatMessage(sessionId, message) {
    const response = await fetch(`/api/chat/sessions/${sessionId}/stream`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let botMessage = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '));

        for (const line of lines) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            const parsed = JSON.parse(data);
            botMessage += parsed.content;
            updateBotMessageUI(botMessage);  // обновляем UI посимвольно
        }
    }
}
```

---

## 5. Промпт-инжиниринг

### System Prompt (шаблон)

```
Ты — персональный шахматный тренер. Твоя задача — помогать игроку улучшать навыки.

ПРОФИЛЬ УЧЕНИКА:
- Имя: {username}
- Уровень: {level}
- ELO рейтинг: {elo_rating}
- Сыграно партий: {total_games} (побед: {wins}, поражений: {losses})
- Слабые темы: {weak_topics}
- Частые ошибки: {common_mistakes}

ПРАВИЛА:
1. Объясняй на уровне, понятном игроку с рейтингом {elo_rating}
2. Используй шахматную нотацию (алгебраическую)
3. Если ученик спрашивает про конкретную партию — анализируй ходы
4. Предлагай конкретные упражнения и планы улучшения
5. Будь мотивирующим, но честным — указывай на ошибки
6. Отвечай на русском языке
7. Если получаешь PGN — анализируй его с привязкой к данным Stockfish
8. НЕ придумывай информацию о партиях — используй только предоставленные данные

{additional_context}
```

### Примеры additional_context

**Для анализа партии:**
```
КОНТЕКСТ ПАРТИИ (ID: {game_id}):
- Дата: {date}
- Противник: {opponent} (бот уровень {bot_level})
- Результат: {result}
- PGN: {pgn}

НАЙДЕННЫЕ ОШИБКИ (Stockfish анализ):
{mistakes_list}
```

**Для обзора прогресса:**
```
ПОСЛЕДНИЕ 5 ПАРТИЙ:
{recent_games_summary}

ТЕКУЩИЙ ПЛАН ОБУЧЕНИЯ:
- Неделя {current_week} из {total_weeks}
- Тема: {current_topic}
- Прогресс: {progress}%
```

---

## 6. Безопасность и лимиты

### API-ключ
- Хранить `OPENAI_API_KEY` **только** в переменных окружения на сервере
- Никогда не отправлять ключ на фронтенд
- Добавить `OPENAI_API_KEY` в `.env` и `.gitignore`

### Rate Limiting
```python
# Глобальный лимит для чата
@limiter.limit("50/day;30/hour", key_func=get_jwt_identity)

# Анализ PGN (дороже по токенам)
@limiter.limit("10/day", key_func=get_jwt_identity)
```

### Защита от инъекций в промпт
- Не вставлять пользовательский текст напрямую в system prompt
- Пользовательские сообщения всегда идут как `role: "user"`, никогда как `role: "system"`
- Валидировать PGN перед парсингом (проверять через `python-chess`)
- Ограничить длину сообщения пользователя (например, 5000 символов)

### Мониторинг расходов
- Записывать `tokens_used` для каждого сообщения в `ChatMessage`
- Создать эндпоинт для админа: GET `/api/admin/chat-stats` — общий расход токенов
- Установить alert при превышении дневного бюджета (через OpenAI dashboard)

---

## 7. Оценка сроков

### Бэкендер

| Этап | Задача | Дни |
|------|--------|-----|
| 1 | Модели + миграции | 1-2 |
| 2 | Сервис контекста | 2-3 |
| 3 | OpenAI интеграция | 2-3 |
| 4 | API роуты | 1-2 |
| 5 | Streaming (опц.) | 2-3 |
| 6 | Тесты | 1-2 |
| **Итого** | | **9-15 дней** |

### Фронтендер

| Этап | Задача | Дни |
|------|--------|-----|
| 1 | Страница чата (UI) | 2-3 |
| 2 | API-функции | 1 |
| 3 | Markdown-рендеринг | 1-2 |
| 4 | Quick actions | 1-2 |
| 5 | Интеграция в страницы | 2-3 |
| 6 | Streaming UI (опц.) | 1-2 |
| **Итого** | | **8-13 дней** |

### Порядок работы (параллельная разработка)

```
Неделя 1:
  Бэкенд: Этапы 1-2 (модели + контекст)
  Фронт:  Этап 1 (UI чата, моковые данные)

Неделя 2:
  Бэкенд: Этапы 3-4 (OpenAI + роуты)
  Фронт:  Этапы 2-3 (API + markdown)

Неделя 3:
  Бэкенд: Этап 6 (тесты) + Этап 5 (streaming)
  Фронт:  Этапы 4-5 (quick actions + интеграция)

Неделя 4:
  Совместно: интеграционное тестирование, фикс багов, streaming UI
```

---

## Зависимости для установки

### Backend (`requirements.txt`):
```
openai>=1.0.0
tiktoken>=0.5.0    # подсчёт токенов до отправки
```

### Frontend (CDN):
```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

---

## Быстрый старт (MVP)

Если нужно запустить минимальную версию за **3-5 дней**:

1. **Бэкенд:** Один эндпоинт `POST /api/chat/quick` — принимает сообщение, собирает базовый контекст (профиль + статистика), отправляет в GPT-4o-mini, возвращает ответ. Без сессий, без истории.

2. **Фронтенд:** Плавающая кнопка на Dashboard → открывает модальное окно с простым чатом (без sidebar, без сессий). Сообщения хранятся только в памяти (пропадают при перезагрузке).

3. Потом итеративно добавлять: сессии → историю → контекст игр → PGN-анализ → streaming → интеграции в страницы.
