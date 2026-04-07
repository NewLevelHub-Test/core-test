import json
from datetime import datetime
from app import create_app, db
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.test_attempt import TestAttempt
from app.models.topic import Topic

# Создаем контекст приложения
app = create_app()

def seed_smart_tests():
    with app.app_context():
        try:
            db.session.query(TestAttempt).delete()
            db.session.query(TestQuestion).delete()
            db.session.query(Test).delete()
            db.session.commit()
            print("Старые тесты и вопросы успешно удалены.")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при очистке: {e}")
            return

        print("--- Обновление/Создание тем (Topics) ---")
        topics_names = ["Основы", "Тактика", "Дебюты", "Миттельшпиль", "Эндшпиль"]
        for i, name in enumerate(topics_names, 1):
            topic = Topic.query.get(i)
            if not topic:
                topic = Topic(id=i, name=name, order=i)
                db.session.add(topic)
            else:
                topic.name = name 
        db.session.commit()

        print("--- Создание Вступительного Теста ---")
        diag_test = Test(
            id=1,
            title="Вступительный тест-диагностика",
            description="Пройди этот тест для определения уровня.",
            difficulty="beginner" 
        )
        db.session.add(diag_test)
        db.session.commit()

        print("--- Наполнение вопросами с FEN-позициями ---")
        
        START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        questions_data = [
            {
                "topic_id": 1, "order": 1,
                "text": "Какая фигура может перепрыгивать через другие фигуры?",
                "options": ["Слон", "Ладья", "Конь", "Ферзь"],
                "correct": "Конь",
                "exp": "Только конь имеет уникальную Г-образную траекторию, позволяющую перепрыгивать фигуры.",
                "fen": "r1bqkbnr/pppppppp/n7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" 
            },
            {
                "topic_id": 1, "order": 2,
                "text": "Возможна ли рокировка, если королю объявлен шах?",
                "options": ["Да", "Нет", "Только в длинную сторону"],
                "correct": "Нет",
                "exp": "Правила запрещают рокировку, если король находится под шахом.",
                "fen": "r3k2r/8/8/8/8/3q4/8/R3K2R w KQkq - 0 1"
            },
            
            {
                "topic_id": 2, "order": 3,
                "text": "Как называется прием, когда одна фигура атакует две цели одновременно?",
                "options": ["Связка", "Вилка", "Цугцванг", "Пат"],
                "correct": "Вилка",
                "exp": "Вилка (двойной удар) — нападение на две и более фигуры сразу.",
                "fen": "r3k2r/p1p2ppp/2p5/2b1p3/6n1/2NP2P1/PPP1PP1P/R1BQK2R w KQkq - 0 1" 
            },
            {
                "topic_id": 2, "order": 4,
                "text": "Что такое 'Связка'?",
                "options": ["Защита короля", "Нападение на фигуру, за которой стоит более ценная фигура", "Размен"],
                "correct": "Нападение на фигуру, за которой стоит более ценная фигура",
                "exp": "Связанная фигура не может ходить, так как подставит под удар более важную фигуру.",
                "fen": "4k3/8/8/8/8/8/R7/4K3 w - - 0 1" 
            },

            {
                "topic_id": 3, "order": 5,
                "text": "Какова главная цель начальной стадии игры (дебюта)?",
                "options": ["Поставить мат", "Развитие фигур и контроль центра", "Вывести ферзя"],
                "correct": "Развитие фигур и контроль центра",
                "exp": "В начале игры важно захватить пространство в центре и подготовить рокировку.",
                "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1" 
            },
            {
                "topic_id": 3, "order": 6,
                "text": "Ход 1... c5 в ответ на 1. e4 характерна для какой защиты?",
                "options": ["Французская", "Сицилианская", "Скандинавская", "Каро-Канн"],
                "correct": "Сицилианская",
                "exp": "1... c5 — это Сицилианская защита, популярный ответ на e4.",
                "fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2" 
            },

            {
                "topic_id": 4, "order": 7,
                "text": "Что такое 'изолированная пешка'?",
                "options": ["Пешка без соседей своего цвета", "Пешка на краю доски", "Пешка у короля"],
                "correct": "Пешка без соседей своего цвета",
                "exp": "Изолированную пешку сложнее защищать, так как её не могут поддержать другие пешки.",
                "fen": "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1" 
            },
            {
                "topic_id": 4, "order": 8,
                "text": "В открытых позициях преимущество обычно на стороне...",
                "options": ["Двух коней", "Двух слонов", "Короля в центре"],
                "correct": "Двух слонов",
                "exp": "Два слона отлично контролируют открытые диагонали на большом расстоянии.",
                "fen": "4k3/8/8/8/8/8/8/4K3 w - - 0 1" 
            },


            {
                "topic_id": 5, "order": 9,
                "text": "Что означает термин 'Цугцванг'?",
                "options": ["Любой ход ведет к ухудшению позиции", "Ничья", "Мат"],
                "correct": "Любой ход ведет к ухудшению позиции",
                "exp": "Игрок обязан ходить, хотя любой ход ослабляет его положение.",
                "fen": "8/8/8/8/8/8/4k3/4K3 b - - 0 1" 
            },
            {
                "topic_id": 5, "order": 10,
                "text": "Как называется ситуация, когда нет шаха, но нет и легальных ходов?",
                "options": ["Мат", "Пат", "Вечный шах"],
                "correct": "Пат",
                "exp": "Пат — это немедленная ничья.",
                "fen": "k7/8/8/8/8/8/7q/K7 w - - 0 1" 
            }
        ]

        questions_objects = []
        for q in questions_data:
            questions_objects.append(TestQuestion(
                test_id=diag_test.id, 
                topic_id=q["topic_id"],
                order=q["order"],
                question_text=q["text"],
                options=q["options"],  
                correct_answer=q["correct"],
                explanation=q["exp"],
                fen=q["fen"]
            ))

        db.session.bulk_save_objects(questions_objects)
        db.session.commit()
        print("--- Успех! База тестов заполнена эталонными вопросами (10 шт.) ---")

if __name__ == "__main__":
    seed_smart_tests()