import os
from app import create_app, db
from app.models.user import User
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.models.test import Test
from app.models.test_question import TestQuestion

def run_seed(app_to_use=None):
    app = app_to_use if app_to_use else create_app()
    
    with app.app_context():
        try:
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin', 
                    email='admin@example.com', 
                    phone='77777777777', 
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)

            topics_data = ["Основы", "Тактика", "Дебюты", "Миттельшпиль", "Эндшпиль"]
            topic_objs = []
            for idx, name in enumerate(topics_data):
                t = Topic.query.filter_by(name=name).first()
                if not t:
                    t = Topic(name=name, order=idx + 1)
                    db.session.add(t)
                    db.session.flush()
                topic_objs.append(t)

            all_lessons = []
            for topic in topic_objs:
                for i in range(1, 4):
                    title = f"{topic.name}: Урок {i}"
                    lesson = Lesson.query.filter_by(title=title, topic_id=topic.id).first()
                    if not lesson:
                        lesson = Lesson(
                            topic_id=topic.id,
                            title=title,
                            content=f"Теория для {topic.name}",
                            theory_cards=[{"title": "Инфо", "text": "Текст теории"}],
                            board_examples=[{"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}],
                            order=i
                        )
                        db.session.add(lesson)
                        db.session.flush()
                    all_lessons.append(lesson)

            if Exercise.query.count() == 0:
                for i in range(1, 31):
                    current_lesson = all_lessons[(i - 1) % len(all_lessons)]
                    ex = Exercise(
                        lesson_id=current_lesson.id,
                        fen="4r1k1/5ppp/2Q5/8/8/8/5PPP/6K1 w - - 0 1",
                        correct_move="Qxe8#",
                        hint="Смотрите на край",
                        explanation="Мат по последней горизонтали",
                        order=i
                    )
                    db.session.add(ex)

            if Test.query.count() == 0:
                for t_idx in range(1, 3):
                    test = Test(title=f"Тест {t_idx}", description="Проверка знаний")
                    db.session.add(test)
                    db.session.flush()

                    for q_idx in range(1, 11):
                        q = TestQuestion(
                            test_id=test.id,
                            question_text=f"Вопрос {q_idx}: Как лучше сходить?",
                            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                            options=["e4", "d4", "Nf3", "c4"],
                            correct_answer="e4", 
                            explanation="Это самый популярный первый ход",
                            order=q_idx
                        )
                        db.session.add(q)

            db.session.commit()
            print("Done: Database seeded successfully.")

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    run_seed()