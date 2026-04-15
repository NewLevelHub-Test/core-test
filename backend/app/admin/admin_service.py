from app import db
from app.models.user import User
from app.models.lesson import Lesson
from app.models.topic import Topic
from app.models.exercise import Exercise
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.test_attempt import TestAttempt
from app.models.game import Game
from app.models.progress import Progress



class AdminService:

    @staticmethod
    def is_admin(user_id):
        user = User.query.get(user_id)
        return user and user.role == 'admin'

    # --- Users ---

    @staticmethod
    def get_all_users(page=1):
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=30, error_out=False
        )
        return {
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        }, 200

    @staticmethod
    def get_user_detail(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        total_games = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).count()

        completed_lessons = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).filter(Progress.lesson_id.isnot(None)).count()

        test_attempts = TestAttempt.query.filter_by(user_id=user_id).count()
        last_test = TestAttempt.query.filter_by(
            user_id=user_id
        ).order_by(TestAttempt.started_at.desc()).first()

        return {
            'user': user.to_dict(),
            'stats': {
                'total_games': total_games,
                'completed_lessons': completed_lessons,
                'test_attempts': test_attempts,
                'last_test': last_test.to_dict() if last_test else None,
            },
        }, 200

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "Пользователь не найден"}, 404

        try:
            from app.models.mistake import Mistake
            from app.models.move import Move
            from app.models.chat import ChatSession

            Mistake.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            Progress.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            TestAttempt.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            ChatSession.query.filter_by(user_id=user_id).delete(synchronize_session=False)

            games = Game.query.filter(
                (Game.white_id == user_id) | (Game.black_id == user_id)
            ).all()
            for game in games:
                Move.query.filter_by(game_id=game.id).delete(synchronize_session=False)
            Game.query.filter(
                (Game.white_id == user_id) | (Game.black_id == user_id)
            ).delete(synchronize_session=False)

            from app.models.roadmap import Roadmap
            from app.models.roadmap_week import RoadmapWeek
            from app.models.daily_task import DailyTask
            roadmaps = Roadmap.query.filter_by(user_id=user_id).all()
            for rm in roadmaps:
                weeks = RoadmapWeek.query.filter_by(roadmap_id=rm.id).all()
                for w in weeks:
                    DailyTask.query.filter_by(week_id=w.id).delete(synchronize_session=False)
                RoadmapWeek.query.filter_by(roadmap_id=rm.id).delete(synchronize_session=False)
            Roadmap.query.filter_by(user_id=user_id).delete(synchronize_session=False)

            db.session.delete(user)
            db.session.commit()
            return {"message": "Пользователь и все связанные данные удалены"}, 200

        except Exception:
            db.session.rollback()
            import logging
            logging.getLogger(__name__).exception("Error deleting user %s", user_id)
            return {"error": "Ошибка удаления пользователя"}, 500
        

    # --- Topics ---

    @staticmethod
    def get_topics(page=1):
        pagination = Topic.query.order_by(Topic.order).paginate(
        page=page, per_page=20, error_out=False
    )
        result = []
        for t in pagination.items:
            d = t.to_dict()
            d['lesson_count'] = Lesson.query.filter_by(topic_id=t.id).count()
            result.append(d)
        return {
        'topics': result,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    }, 200

    @staticmethod
    def create_topic(data):
        topic = Topic(
            name=data['name'],
            description=data.get('description', ''),
            order=data.get('order', 0),
        )
        db.session.add(topic)
        db.session.commit()
        return {'topic': topic.to_dict()}, 201

    @staticmethod
    def update_topic(topic_id, data):
        topic = Topic.query.get(topic_id)
        if not topic:
            return {'error': 'Тема не найдена'}, 404
        if 'name' in data:
            topic.name = data['name']
        if 'description' in data:
            topic.description = data['description']
        if 'order' in data:
            topic.order = data['order']
        db.session.commit()
        return {'topic': topic.to_dict()}, 200

    @staticmethod
    def delete_topic(topic_id):
        topic = Topic.query.get(topic_id)
        if not topic:
            return {'error': 'Тема не найдена'}, 404
        db.session.delete(topic)
        db.session.commit()
        return {'message': 'Тема удалена'}, 200

    # --- Lessons ---

    @staticmethod
    def create_lesson(data):
        lesson = Lesson(
            topic_id=data['topic_id'],
            title=data['title'],
            content=data.get('content', ''),
            theory_cards=data.get('theory_cards'),
            board_examples=data.get('board_examples'),
            difficulty=data.get('difficulty', 'beginner'),
            order=data.get('order', 0),
        )
        db.session.add(lesson)
        db.session.commit()
        return {'lesson': lesson.to_dict()}, 201

    @staticmethod
    def update_lesson(lesson_id, data):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'error': 'Урок не найден'}, 404
        for field in ('title', 'content', 'theory_cards', 'board_examples', 'difficulty', 'order', 'topic_id'):
            if field in data:
                setattr(lesson, field, data[field])
        db.session.commit()
        return {'lesson': lesson.to_dict()}, 200

    @staticmethod
    def delete_lesson(lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'error': 'Урок не найден'}, 404
        db.session.delete(lesson)
        db.session.commit()
        return {'message': 'Урок удалён'}, 200

    # --- Exercises ---

    @staticmethod
    def create_exercise(data):
        exercise = Exercise(
            lesson_id=data['lesson_id'],
            fen=data['fen'],
            correct_move=data['correct_move'],
            hint=data.get('hint'),
            explanation=data.get('explanation'),
            difficulty=data.get('difficulty', 'beginner'),
            order=data.get('order', 0),
        )
        db.session.add(exercise)
        db.session.commit()
        return {'exercise': exercise.to_dict()}, 201

    @staticmethod
    def update_exercise(exercise_id, data):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Упражнение не найдено'}, 404
        for field in ('fen', 'correct_move', 'hint', 'explanation', 'difficulty', 'order', 'lesson_id'):
            if field in data:
                setattr(exercise, field, data[field])
        db.session.commit()
        return {'exercise': exercise.to_dict()}, 200

    @staticmethod
    def delete_exercise(exercise_id):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Упражнение не найдено'}, 404
        db.session.delete(exercise)
        db.session.commit()
        return {'message': 'Упражнение удалено'}, 200

    @staticmethod
    def get_all_exercises(page=1, per_page=20):
        pagination = Exercise.query.order_by(Exercise.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            'exercises': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }, 200

    # --- Tests & Questions ---

    @staticmethod
    def create_test(data):
        test = Test(
            title=data['title'],
            description=data.get('description', ''),
            topic_id=data.get('topic_id'),
            difficulty=data.get('difficulty', 'beginner'),
            time_limit=data.get('time_limit'),
        )
        db.session.add(test)
        db.session.flush()

        for q_data in data.get('questions', []):
            question = TestQuestion(
                test_id=test.id,
                question_text=q_data['question_text'],
                fen=q_data.get('fen'),
                options=q_data.get('options'),
                correct_answer=q_data['correct_answer'],
                explanation=q_data.get('explanation'),
                order=q_data.get('order', 0),
            )
            db.session.add(question)

        db.session.commit()
        return {'test': test.to_dict()}, 201

    @staticmethod
    def update_test(test_id, data):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404
        for field in ('title', 'description', 'topic_id', 'difficulty', 'time_limit'):
            if field in data:
                setattr(test, field, data[field])
        db.session.commit()
        return {'test': test.to_dict()}, 200

    @staticmethod
    def add_question(test_id, data):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404

        question = TestQuestion(
            test_id=test_id,
            question_text=data['question_text'],
            fen=data.get('fen'),
            options=data.get('options'),
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation'),
            order=data.get('order', 0),
        )
        db.session.add(question)
        db.session.commit()
        return {'question': question.to_dict()}, 201

    @staticmethod
    def update_question(question_id, data):
        question = TestQuestion.query.get(question_id)
        if not question:
            return {'error': 'Вопрос не найден'}, 404
        for field in ('question_text', 'fen', 'options', 'correct_answer', 'explanation', 'order'):
            if field in data:
                setattr(question, field, data[field])
        db.session.commit()
        return {'question': question.to_dict()}, 200

    @staticmethod
    def delete_question(question_id):
        question = TestQuestion.query.get(question_id)
        if not question:
            return {'error': 'Вопрос не найден'}, 404
        db.session.delete(question)
        db.session.commit()
        return {'message': 'Вопрос удалён'}, 200

    @staticmethod
    def get_test_detail(test_id):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404
        questions = TestQuestion.query.filter_by(test_id=test_id).order_by(TestQuestion.order).all()
        return {
            'test': test.to_dict(),
            'questions': [q.to_dict() for q in questions],
        }, 200

    @staticmethod
    def delete_test(test_id):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404
        TestQuestion.query.filter_by(test_id=test_id).delete()
        TestAttempt.query.filter_by(test_id=test_id).delete()
        db.session.delete(test)
        db.session.commit()
        return {'message': 'Тест удалён'}, 200

    # --- Platform Stats ---

    @staticmethod
    def get_platform_stats():
        return {
            'total_users': User.query.count(),
            'total_games': Game.query.count(),
            'total_lessons': Lesson.query.count(),
            'total_topics': Topic.query.count(),
            'total_exercises': Exercise.query.count(),
            'total_tests': Test.query.count(),
            'total_test_attempts': TestAttempt.query.count(),
        }, 200
