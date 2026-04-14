"""
Seed script — creates admin, topics, lessons, exercises, and tests.
Run: python seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app, db
from app.models.user import User
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.models.test import Test
from app.models.test_question import TestQuestion

app = create_app()

TOPICS = [
    {"name": "Дебюты", "description": "Начальная стадия партии — первые 10-15 ходов", "order": 1},
    {"name": "Тактика", "description": "Комбинации и приёмы: вилки, связки, открытые атаки", "order": 2},
    {"name": "Стратегия", "description": "Долгосрочные планы и позиционная игра", "order": 3},
    {"name": "Эндшпиль", "description": "Заключительная стадия партии", "order": 4},
    {"name": "Мат в 1 ход", "description": "Учимся ставить мат за один ход", "order": 5},
    {"name": "Мат в 2 хода", "description": "Комбинации для мата в два хода", "order": 6},
    {"name": "Пешечная структура", "description": "Сильные и слабые пешки, цепочки, островки", "order": 7},
    {"name": "Атака на короля", "description": "Как атаковать позицию рокировки", "order": 8},
    {"name": "Защита", "description": "Как защищаться от атак соперника", "order": 9},
    {"name": "Шахматные окончания", "description": "Ладейные, пешечные и лёгкофигурные окончания", "order": 10},
]

LESSONS_BY_TOPIC = {
    "Дебюты": [
        {
            "title": "Итальянская партия",
            "content": "Итальянская партия начинается ходами 1.e4 e5 2.Кf3 Кc6 3.Сc4. Белые быстро выводят лёгкие фигуры и нацеливаются на слабое поле f7. Это один из самых древних и популярных дебютов.",
            "theory_cards": [
                {"title": "Основная идея", "text": "Контроль центра и быстрое развитие фигур"},
                {"title": "Ключевые ходы", "text": "1.e4 e5 2.Кf3 Кc6 3.Сc4"},
                {"title": "План", "text": "Вывести фигуры, сделать рокировку, атаковать центр"}
            ],
            "board_examples": [
                {"fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3", "description": "Позиция после 3.Сc4"},
                {"fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "description": "Чёрные ответили 3...Сc5 (Giuoco Piano)"}
            ],
            "difficulty": "beginner", "order": 1
        },
        {
            "title": "Испанская партия (Руй Лопес)",
            "content": "Испанская партия: 1.e4 e5 2.Кf3 Кc6 3.Сb5. Белые атакуют коня, который защищает пешку e5. Это самый популярный дебют в мировых чемпионатах.",
            "theory_cards": [
                {"title": "Основная идея", "text": "Давление на пешку e5 через атаку коня c6"},
                {"title": "Ключевые ходы", "text": "1.e4 e5 2.Кf3 Кc6 3.Сb5"}
            ],
            "board_examples": [
                {"fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3", "description": "Позиция после 3.Сb5"}
            ],
            "difficulty": "beginner", "order": 2
        },
        {
            "title": "Сицилианская защита",
            "content": "1.e4 c5 — самый популярный ответ за чёрных. Чёрные борются за центр пешкой c, создавая асимметричную позицию с шансами для обеих сторон.",
            "theory_cards": [
                {"title": "Идея", "text": "Чёрные борются за поле d4 не через e5, а через c5"},
                {"title": "Варианты", "text": "Найдорф, Дракон, Схевенинген — популярные системы"}
            ],
            "board_examples": [
                {"fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", "description": "После 1...c5"}
            ],
            "difficulty": "intermediate", "order": 3
        },
    ],
    "Тактика": [
        {
            "title": "Вилка",
            "content": "Вилка — это ход, при котором одна фигура атакует сразу две или более фигуры противника. Чаще всего вилки ставят кони, потому что они перепрыгивают через другие фигуры.",
            "theory_cards": [
                {"title": "Что такое вилка", "text": "Одна фигура нападает на две фигуры соперника одновременно"},
                {"title": "Конь-мастер вилок", "text": "Конь — лучший для вилок, его трудно заблокировать"}
            ],
            "board_examples": [
                {"fen": "r1bqkb1r/pppp1ppp/2n2n2/4N3/4P3/8/PPPP1PPP/RNBQKB1R b KQkq - 0 1", "description": "Конь на e5 атакует f7 и c6"}
            ],
            "difficulty": "beginner", "order": 1
        },
        {
            "title": "Связка",
            "content": "Связка — это когда фигура не может двигаться, потому что за ней стоит более ценная фигура. Различают абсолютную связку (за фигурой король) и относительную.",
            "theory_cards": [
                {"title": "Абсолютная связка", "text": "Фигура не может пойти — за ней король"},
                {"title": "Относительная связка", "text": "Фигура может пойти, но тогда теряется более ценная"}
            ],
            "board_examples": [
                {"fen": "rnbqk2r/ppppbppp/4pn2/8/3PP3/2N2N2/PPP2PPP/R1BQKB1R b KQkq - 0 1", "description": "Слон может связать коня"}
            ],
            "difficulty": "beginner", "order": 2
        },
        {
            "title": "Двойной удар",
            "content": "Двойной удар — атака на две фигуры одновременно. Это может быть шах + нападение на фигуру, или нападение на две незащищённые фигуры.",
            "theory_cards": [
                {"title": "Типы двойных ударов", "text": "Шах + взятие, нападение на две фигуры, открытое нападение"}
            ],
            "board_examples": [
                {"fen": "r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/5N2/PPPP1PPP/RNBQ1RK1 w kq - 0 1", "description": "Белые могут создать двойной удар"}
            ],
            "difficulty": "beginner", "order": 3
        },
    ],
    "Мат в 1 ход": [
        {
            "title": "Мат ладьёй",
            "content": "Ладья — сильная фигура. Она может дать мат, прижав короля к краю доски. Нужно отрезать королю пути отступления.",
            "theory_cards": [
                {"title": "Принцип", "text": "Прижать короля к краю, дать шах ладьёй по крайней линии"}
            ],
            "board_examples": [
                {"fen": "6k1/8/6K1/8/8/8/8/R7 w - - 0 1", "description": "Белые: Ла8 — мат!"}
            ],
            "difficulty": "beginner", "order": 1
        },
        {
            "title": "Мат ферзём",
            "content": "Ферзь — самая сильная фигура. Он может давать мат разными способами. Но помни — нельзя ставить ферзя слишком близко к королю без поддержки, иначе его заберут!",
            "theory_cards": [
                {"title": "Правило", "text": "Ферзь + помощник (другая фигура или пешка) = мат"}
            ],
            "board_examples": [
                {"fen": "7k/8/5K2/8/8/8/8/1Q6 w - - 0 1", "description": "Белые: Фb8 — мат!"}
            ],
            "difficulty": "beginner", "order": 2
        },
    ],
    "Эндшпиль": [
        {
            "title": "Пешечные окончания",
            "content": "В пешечных окончаниях нет фигур кроме королей и пешек. Здесь очень важна активность короля и правило квадрата — поможет понять, успеет ли пешка пройти в ферзи.",
            "theory_cards": [
                {"title": "Правило квадрата", "text": "Если король попадает в квадрат пешки — он её ловит"},
                {"title": "Оппозиция", "text": "Кто стоит в оппозиции — тот имеет преимущество"}
            ],
            "board_examples": [
                {"fen": "8/8/8/3k4/8/8/3PK3/8 w - - 0 1", "description": "Пешечное окончание с оппозицией"}
            ],
            "difficulty": "intermediate", "order": 1
        },
        {
            "title": "Ладья + пешка vs ладья",
            "content": "Самый частый тип эндшпиля. Нужно знать позицию Лусены (как выиграть) и позицию Филидора (как защищаться).",
            "theory_cards": [
                {"title": "Позиция Лусены", "text": "Пешка на 7-й линии + мост ладьёй = выигрыш"},
                {"title": "Позиция Филидора", "text": "Ладья на 6-й линии не пускает короля = ничья"}
            ],
            "board_examples": [
                {"fen": "8/4R1pk/8/8/8/8/4P3/4K2r w - - 0 1", "description": "Ладейный эндшпиль"}
            ],
            "difficulty": "intermediate", "order": 2
        },
    ],
    "Стратегия": [
        {
            "title": "Контроль центра",
            "content": "Центральные поля e4, d4, e5, d5 — самые важные. Фигуры в центре контролируют больше клеток и могут быстро перебраться на любой фланг.",
            "theory_cards": [
                {"title": "Центральные поля", "text": "e4, d4, e5, d5 — ключевые точки доски"},
                {"title": "Принцип", "text": "Контролируй центр пешками и фигурами"}
            ],
            "board_examples": [
                {"fen": "rnbqkbnr/pppppppp/8/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 2", "description": "Идеальный пешечный центр белых"}
            ],
            "difficulty": "beginner", "order": 1
        },
    ],
    "Пешечная структура": [
        {
            "title": "Изолированные и сдвоенные пешки",
            "content": "Изолированная пешка — та, рядом с которой нет своих пешек на соседних вертикалях. Сдвоенные пешки — две пешки на одной вертикали. Обе — слабости.",
            "theory_cards": [
                {"title": "Изолятор", "text": "Пешка без соседей — её трудно защищать"},
                {"title": "Сдвоенные", "text": "Две пешки на одной линии мешают друг другу"}
            ],
            "board_examples": [
                {"fen": "rnbqkbnr/pp2pppp/8/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3", "description": "Пешечная структура после размена"}
            ],
            "difficulty": "intermediate", "order": 1
        },
    ],
    "Атака на короля": [
        {
            "title": "Жертва на h7",
            "content": "Классическая жертва слона на h7 — один из самых известных приёмов. Слон бьёт на h7 с шахом, потом конь идёт на g5, и начинается атака.",
            "theory_cards": [
                {"title": "Условия", "text": "Слон на d3, конь на f3, ферзь готов подключиться"},
                {"title": "Ход", "text": "Сxh7+! Крxh7, Кg5+ и далее Фh5"}
            ],
            "board_examples": [
                {"fen": "r1bq1rk1/pppn1ppp/4pn2/3p4/3P4/3BPN2/PPP2PPP/R1BQ1RK1 w - - 0 1", "description": "Классическая позиция для жертвы на h7"}
            ],
            "difficulty": "intermediate", "order": 1
        },
    ],
    "Защита": [
        {
            "title": "Профилактика",
            "content": "Лучшая защита — это когда ты заранее видишь угрозу и предотвращаешь её. Спрашивай себя на каждом ходу: что хочет соперник?",
            "theory_cards": [
                {"title": "Вопрос", "text": "Что соперник хотел своим последним ходом?"},
                {"title": "Совет", "text": "Думай не только о своих ходах, но и об угрозах соперника"}
            ],
            "board_examples": [
                {"fen": "r1bqkbnr/pppppppp/2n5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2", "description": "Обычная позиция — подумай, что хотят чёрные?"}
            ],
            "difficulty": "beginner", "order": 1
        },
    ],
    "Мат в 2 хода": [
        {
            "title": "Комбинации с шахом",
            "content": "Мат в 2 хода обычно начинается с шаха или сильной угрозы. Первый ход создаёт неотразимую угрозу, второй — ставит мат.",
            "theory_cards": [
                {"title": "Алгоритм", "text": "1. Найди шахи и угрозы. 2. Проверь, ведёт ли один из них к мату через ход"}
            ],
            "board_examples": [
                {"fen": "r1b1k2r/ppppqppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 1", "description": "Ищи мат в 2 хода"}
            ],
            "difficulty": "beginner", "order": 1
        },
    ],
    "Шахматные окончания": [
        {
            "title": "Король и ферзь против короля",
            "content": "Это базовый мат, который нужно уметь ставить. План: ферзь оттесняет короля к краю, твой король помогает, потом — мат.",
            "theory_cards": [
                {"title": "План", "text": "1. Отрезать короля ферзём. 2. Подвести своего короля. 3. Мат на краю."},
                {"title": "Важно", "text": "Не ставь пат! Оставляй сопернику хотя бы один ход."}
            ],
            "board_examples": [
                {"fen": "8/8/8/4k3/8/8/4K3/4Q3 w - - 0 1", "description": "Мат ферзём — начальная позиция"}
            ],
            "difficulty": "beginner", "order": 1
        },
    ],
}

EXERCISES_BY_LESSON = {
    "Итальянская партия": [
        {"fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3", "correct_move": "Bc5", "hint": "Выведи слона на активную позицию", "difficulty": "beginner"},
        {"fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "correct_move": "c3", "hint": "Подготовь продвижение d4", "difficulty": "beginner"},
        {"fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2BPP3/5N2/PPP2PPP/RNBQK2R b KQkq d3 0 4", "correct_move": "exd4", "hint": "Возьми пешку в центре", "difficulty": "beginner"},
    ],
    "Вилка": [
        {"fen": "r1bqkb1r/ppppnppp/5n2/4p1N1/2B1P3/8/PPPP1PPP/RNBQK2R w KQkq - 0 1", "correct_move": "Nxf7", "hint": "Конь может напасть на ферзя и ладью", "difficulty": "beginner"},
        {"fen": "r2qkb1r/ppp2ppp/2n1bn2/3pp3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 1", "correct_move": "Nxe5", "hint": "После взятия конь окажется на вилке", "difficulty": "beginner"},
    ],
    "Связка": [
        {"fen": "rn1qkbnr/ppp1pppp/3p4/8/3PP1b1/5N2/PPP2PPP/RNBQKB1R w KQkq - 1 4", "correct_move": "Be2", "hint": "Развей слона и разорви связку", "difficulty": "beginner"},
    ],
    "Двойной удар": [
        {"fen": "r2q1rk1/ppp1bppp/2n1bn2/3p4/3P4/2NBPN2/PPP2PPP/R1BQ1RK1 w - - 0 1", "correct_move": "Nb5", "hint": "Конь нападает на c7 и d6", "difficulty": "intermediate"},
    ],
    "Мат ладьёй": [
        {"fen": "6k1/8/6K1/8/8/8/8/R7 w - - 0 1", "correct_move": "Ra8", "hint": "Ладья на 8-ю линию — мат!", "difficulty": "beginner"},
        {"fen": "k7/8/1K6/8/8/8/8/7R w - - 0 1", "correct_move": "Ra1", "hint": "Мат ладьёй по линии a", "difficulty": "beginner"},
    ],
    "Мат ферзём": [
        {"fen": "7k/8/5K2/8/8/8/8/1Q6 w - - 0 1", "correct_move": "Qb8", "hint": "Ферзь на b8 — мат!", "difficulty": "beginner"},
    ],
    "Пешечные окончания": [
        {"fen": "8/8/8/8/3k4/8/4PK2/8 w - - 0 1", "correct_move": "e4", "hint": "Продвинь пешку", "difficulty": "intermediate"},
    ],
    "Контроль центра": [
        {"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", "correct_move": "e5", "hint": "Займи центр пешкой", "difficulty": "beginner"},
    ],
    "Жертва на h7": [
        {"fen": "r1bq1rk1/pppn1ppp/4pn2/3p4/3P4/3BPN2/PPP2PPP/R1BQ1RK1 w - - 0 1", "correct_move": "Bxh7+", "hint": "Жертва слона на h7 с шахом!", "difficulty": "intermediate"},
    ],
    "Комбинации с шахом": [
        {"fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1", "correct_move": "Re8", "hint": "Ладья на 8-ю — мат!", "difficulty": "beginner"},
    ],
}

TEST_QUESTIONS = [
    {"question_text": "Как называется ход, при котором одна фигура атакует две фигуры соперника?", "options": ["Вилка", "Связка", "Рокировка", "Гамбит"], "correct_answer": "Вилка", "fen": None, "topic_key": "Тактика"},
    {"question_text": "Какая фигура самая сильная в шахматах?", "options": ["Ладья", "Слон", "Ферзь", "Конь"], "correct_answer": "Ферзь", "fen": None, "topic_key": None},
    {"question_text": "Что такое рокировка?", "options": ["Ход королём на 2 клетки и перестановка ладьи", "Превращение пешки", "Взятие на проходе", "Двойной ход пешкой"], "correct_answer": "Ход королём на 2 клетки и перестановка ладьи", "fen": None, "topic_key": None},
    {"question_text": "Какой лучший ход для белых?", "options": ["Ra8#", "Rb1", "Kf7", "Ra2"], "correct_answer": "Ra8#", "fen": "6k1/8/6K1/8/8/8/8/R7 w - - 0 1", "topic_key": "Мат в 1 ход"},
    {"question_text": "Сколько стоит конь (в пешечных единицах)?", "options": ["1", "3", "5", "9"], "correct_answer": "3", "fen": None, "topic_key": None},
    {"question_text": "Как называется начальная стадия партии?", "options": ["Дебют", "Миттельшпиль", "Эндшпиль", "Гамбит"], "correct_answer": "Дебют", "fen": None, "topic_key": "Дебюты"},
    {"question_text": "Что делать в эндшпиле?", "options": ["Активизировать короля", "Спрятать короля за пешки", "Не двигать пешки", "Разменять все фигуры"], "correct_answer": "Активизировать короля", "fen": None, "topic_key": "Эндшпиль"},
    {"question_text": "Какой лучший ход? (Мат в 1 ход)", "options": ["Qb8#", "Qg6", "Qa1", "Kf7"], "correct_answer": "Qb8#", "fen": "7k/8/5K2/8/8/8/8/1Q6 w - - 0 1", "topic_key": "Мат в 1 ход"},
    {"question_text": "Что такое связка?", "options": ["Фигура не может двигаться из-за более ценной за ней", "Ход двумя фигурами", "Атака на две фигуры", "Защита короля"], "correct_answer": "Фигура не может двигаться из-за более ценной за ней", "fen": None, "topic_key": "Тактика"},
    {"question_text": "Какие центральные поля самые важные?", "options": ["a1, a8, h1, h8", "e4, d4, e5, d5", "c3, f3, c6, f6", "b2, g2, b7, g7"], "correct_answer": "e4, d4, e5, d5", "fen": None, "topic_key": "Стратегия"},
    {"question_text": "Что такое пат?", "options": ["Ничья — королю некуда ходить и нет шаха", "Мат", "Двойной удар", "Рокировка"], "correct_answer": "Ничья — королю некуда ходить и нет шаха", "fen": None, "topic_key": None},
    {"question_text": "Какая начальная расстановка правильная для белого коня?", "options": ["b1 и g1", "c1 и f1", "a1 и h1", "d1 и e1"], "correct_answer": "b1 и g1", "fen": None, "topic_key": None},
]


def seed():
    with app.app_context():
        db.create_all()

        # --- Admin user ---
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@rochess.kz', role='admin', age=12, level='advanced')
            admin.set_password('Admin123')
            db.session.add(admin)
            db.session.commit()
            print(f"[+] Admin created (id={admin.id}, login=admin@rochess.kz / Admin123)")
        else:
            print(f"[=] Admin exists (id={admin.id})")

        # --- Test student ---
        student = User.query.filter_by(username='student1').first()
        if not student:
            student = User(username='student1', email='student@test.kz', role='student', age=8, level='beginner')
            student.set_password('Student123')
            db.session.add(student)
            db.session.commit()
            print(f"[+] Student created (id={student.id}, login=student@test.kz / Student123)")
        else:
            print(f"[=] Student exists (id={student.id})")

        # --- Topics ---
        topic_map = {}
        for t_data in TOPICS:
            topic = Topic.query.filter_by(name=t_data['name']).first()
            if not topic:
                topic = Topic(**t_data)
                db.session.add(topic)
                db.session.flush()
                print(f"[+] Topic: {topic.name} (id={topic.id})")
            else:
                print(f"[=] Topic exists: {topic.name}")
            topic_map[topic.name] = topic

        db.session.commit()

        # --- Lessons ---
        lesson_map = {}
        for topic_name, lessons in LESSONS_BY_TOPIC.items():
            topic = topic_map.get(topic_name)
            if not topic:
                continue
            for l_data in lessons:
                lesson = Lesson.query.filter_by(title=l_data['title'], topic_id=topic.id).first()
                if not lesson:
                    lesson = Lesson(
                        topic_id=topic.id,
                        title=l_data['title'],
                        content=l_data['content'],
                        theory_cards=l_data.get('theory_cards'),
                        board_examples=l_data.get('board_examples'),
                        difficulty=l_data.get('difficulty', 'beginner'),
                        order=l_data.get('order', 0),
                    )
                    db.session.add(lesson)
                    db.session.flush()
                    print(f"  [+] Lesson: {lesson.title} (id={lesson.id})")
                else:
                    print(f"  [=] Lesson exists: {lesson.title}")
                lesson_map[lesson.title] = lesson

        db.session.commit()

        # --- Exercises ---
        ex_count = 0
        for lesson_title, exercises in EXERCISES_BY_LESSON.items():
            lesson = lesson_map.get(lesson_title)
            if not lesson:
                continue
            for ex_data in exercises:
                exists = Exercise.query.filter_by(lesson_id=lesson.id, fen=ex_data['fen']).first()
                if not exists:
                    ex = Exercise(
                        lesson_id=lesson.id,
                        fen=ex_data['fen'],
                        correct_move=ex_data['correct_move'],
                        hint=ex_data.get('hint'),
                        difficulty=ex_data.get('difficulty', 'beginner'),
                        order=ex_count,
                    )
                    db.session.add(ex)
                    ex_count += 1

        db.session.commit()
        print(f"[+] Exercises created: {ex_count}")

        # --- Test ---
        test = Test.query.filter_by(title='Тест определения уровня').first()
        if not test:
            test = Test(
                title='Тест определения уровня',
                description='Ответь на вопросы, чтобы мы определили твой уровень и слабые темы',
                difficulty='beginner',
                time_limit=600,
            )
            db.session.add(test)
            db.session.flush()
            print(f"[+] Test created: {test.title} (id={test.id})")

            for i, q_data in enumerate(TEST_QUESTIONS):
                topic_id = None
                if q_data.get('topic_key') and q_data['topic_key'] in topic_map:
                    topic_id = topic_map[q_data['topic_key']].id

                q = TestQuestion(
                    test_id=test.id,
                    question_text=q_data['question_text'],
                    fen=q_data.get('fen'),
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    topic_id=topic_id,
                    order=i,
                )
                db.session.add(q)

            db.session.commit()
            print(f"  [+] Questions added: {len(TEST_QUESTIONS)}")
        else:
            print(f"[=] Test exists: {test.title}")

        print("\n=== SEED COMPLETE ===")
        print(f"Topics: {Topic.query.count()}")
        print(f"Lessons: {Lesson.query.count()}")
        print(f"Exercises: {Exercise.query.count()}")
        print(f"Tests: {Test.query.count()}")
        print(f"Questions: {TestQuestion.query.count()}")
        print(f"Users: {User.query.count()}")


if __name__ == '__main__':
    seed()
