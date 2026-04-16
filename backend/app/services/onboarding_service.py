import logging
from app import db
from app.models.user import User, LEVELS, LEVEL_NAMES_RU
from app.models.game import Game
from app.models.move import Move

logger = logging.getLogger(__name__)

PLACEMENT_QUESTIONS = [
    {
        "id": 1,
        "question": "Какая фигура ходит буквой 'Г'?",
        "options": ["Слон", "Конь", "Ладья", "Ферзь"],
        "correct": 1,
    },
    {
        "id": 2,
        "question": "Сколько клеток на шахматной доске?",
        "options": ["32", "48", "64", "81"],
        "correct": 2,
    },
    {
        "id": 3,
        "question": "Какая фигура самая ценная после короля?",
        "options": ["Ладья", "Конь", "Ферзь", "Слон"],
        "correct": 2,
    },
    {
        "id": 4,
        "question": "Что такое рокировка?",
        "options": [
            "Взятие пешки на проходе",
            "Одновременный ход короля и ладьи",
            "Превращение пешки в ферзя",
            "Шах двумя фигурами одновременно",
        ],
        "correct": 1,
    },
    {
        "id": 5,
        "question": "Какое минимальное количество фигур (кроме королей) нужно для мата?",
        "options": ["1", "2", "3", "0"],
        "correct": 0,
    },
    {
        "id": 6,
        "question": "Что такое 'вилка' в шахматах?",
        "options": [
            "Защита двух фигур одновременно",
            "Нападение одной фигурой на две и более фигур противника",
            "Размен равноценных фигур",
            "Ход пешкой на два поля",
        ],
        "correct": 1,
    },
    {
        "id": 7,
        "question": "В какой дебютной системе белые играют 1.e4 e5 2.Кf3 Кc6 3.Сc4?",
        "options": [
            "Сицилианская защита",
            "Французская защита",
            "Итальянская партия",
            "Защита Каро-Канн",
        ],
        "correct": 2,
    },
    {
        "id": 8,
        "question": "Что такое 'связка' в шахматах?",
        "options": [
            "Фигура не может двинуться, т.к. откроет короля для шаха",
            "Две пешки стоят рядом на одной горизонтали",
            "Ладья стоит на открытой вертикали",
            "Конь блокирует проходную пешку",
        ],
        "correct": 0,
    },
    {
        "id": 9,
        "question": "Что такое оппозиция в пешечном эндшпиле?",
        "options": [
            "Пешки стоят друг напротив друга",
            "Короли стоят друг напротив друга через одну клетку",
            "Ладьи стоят на одной линии",
            "Слоны контролируют одну диагональ",
        ],
        "correct": 1,
    },
    {
        "id": 10,
        "question": "Позиция Лусены — классический приём в каком типе окончаний?",
        "options": ["Пешечных", "Слоновых", "Ладейных", "Ферзевых"],
        "correct": 2,
    },
]


def get_placement_test():
    safe = []
    for q in PLACEMENT_QUESTIONS:
        safe.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
        })
    return safe


def grade_placement_test(answers):
    """answers: list of ints (selected option index) in order of question id."""
    correct = 0
    results = []
    for i, q in enumerate(PLACEMENT_QUESTIONS):
        user_ans = answers[i] if i < len(answers) else -1
        is_ok = user_ans == q["correct"]
        if is_ok:
            correct += 1
        results.append({
            "question": q["question"],
            "user_answer": user_ans,
            "correct_answer": q["correct"],
            "is_correct": is_ok,
        })
    return correct, results


def compute_game_score(game):
    """Evaluate placement game performance: 0-10."""
    if not game or game.status != 'finished':
        return 0

    move_count = game.moves.count()

    result_text = game.result_text
    if result_text == 'win':
        base = 8
    elif result_text == 'draw':
        base = 5
    else:
        base = 2

    if move_count >= 20:
        base += 1
    if move_count >= 40:
        base += 1

    return min(base, 10)


def assign_level(test_score, game_score):
    """test_score: 0-10, game_score: 0-10 → combined 0-20 → level."""
    total = test_score + game_score
    if total <= 4:
        return 'pawn'
    elif total <= 8:
        return 'knight'
    elif total <= 12:
        return 'bishop'
    elif total <= 16:
        return 'rook'
    else:
        return 'queen'


class OnboardingService:

    @staticmethod
    def get_test():
        return {"questions": get_placement_test()}, 200

    @staticmethod
    def submit_test(user_id, answers):
        user = db.session.get(User, int(user_id))
        if not user:
            return {"error": "Пользователь не найден"}, 404

        score, results = grade_placement_test(answers)
        user.placement_test_score = score
        db.session.commit()

        return {
            "score": score,
            "total": len(PLACEMENT_QUESTIONS),
            "results": results,
        }, 200

    @staticmethod
    def start_placement_game(user_id):
        from app.services.game_service import GameService

        data = {
            "mode": "ai",
            "color": "white",
            "bot_level": 2,
            "time_control": 300,
        }
        result, status = GameService.create_game(user_id, data)
        if status == 201 and "game" in result:
            user = db.session.get(User, int(user_id))
            if user:
                user.placement_game_id = result["game"]["id"]
                db.session.commit()
        return result, status

    @staticmethod
    def complete_onboarding(user_id):
        user = db.session.get(User, int(user_id))
        if not user:
            return {"error": "Пользователь не найден"}, 404

        if user.onboarding_completed:
            return {"error": "Онбординг уже завершён"}, 400

        test_score = user.placement_test_score or 0

        game_score = 0
        game_summary = None
        if user.placement_game_id:
            game = db.session.get(Game, user.placement_game_id)
            if game and game.status == 'finished':
                game_score = compute_game_score(game)
                game_summary = {
                    "result": game.result_text,
                    "moves": game.moves.count(),
                    "game_score": game_score,
                }

        level = assign_level(test_score, game_score)
        user.level = level
        user.onboarding_completed = True
        db.session.commit()

        from app.services.roadmap_service import RoadmapService
        RoadmapService.generate_roadmap(str(user.id), level)

        return {
            "level": level,
            "level_name": LEVEL_NAMES_RU.get(level, level),
            "test_score": test_score,
            "game_score": game_score,
            "game_summary": game_summary,
            "total_score": test_score + game_score,
        }, 200
