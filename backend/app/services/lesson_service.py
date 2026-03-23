from datetime import datetime

from app import db
from app.models.lesson import Lesson
from app.models.topic import Topic
from app.models.exercise import Exercise
from app.models.progress import Progress


class LessonService:

    @staticmethod
    def get_topics():
        topics = Topic.query.order_by(Topic.order).all()
        result = []
        for t in topics:
            d = t.to_dict()
            d['lesson_count'] = Lesson.query.filter_by(topic_id=t.id).count()
            result.append(d)
        return {'topics': result}, 200

    @staticmethod
    def get_lessons(topic_id=None):
        query = Lesson.query
        if topic_id:
            query = query.filter_by(topic_id=topic_id)
        lessons = query.order_by(Lesson.order).all()
        return {'lessons': [l.to_dict() for l in lessons]}, 200

    @staticmethod
    def get_lesson_full(lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'error': 'Урок не найден'}, 404

        exercises = Exercise.query.filter_by(
            lesson_id=lesson_id
        ).order_by(Exercise.order).all()

        data = lesson.to_dict()
        data['exercises'] = [e.to_dict() for e in exercises]
        data['topic'] = lesson.topic.to_dict() if lesson.topic else None

        return {'lesson': data}, 200

    @staticmethod
    def get_exercises(lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'error': 'Урок не найден'}, 404

        exercises = Exercise.query.filter_by(
            lesson_id=lesson_id
        ).order_by(Exercise.order).all()

        safe = []
        for e in exercises:
            d = e.to_dict()
            del d['correct_move']
            safe.append(d)

        return {'exercises': safe}, 200

    @staticmethod
    def check_exercise(user_id, exercise_id, user_move):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Упражнение не найдено'}, 404

        is_correct = user_move == exercise.correct_move

        progress = Progress.query.filter_by(
            user_id=user_id, exercise_id=exercise_id
        ).first()
        if not progress:
            progress = Progress(
                user_id=user_id,
                exercise_id=exercise_id,
                lesson_id=exercise.lesson_id,
                status='completed' if is_correct else 'in_progress',
                score=1 if is_correct else 0,
                completed_at=datetime.utcnow() if is_correct else None,
            )
            db.session.add(progress)
        elif is_correct:
            progress.status = 'completed'
            progress.score = 1
            progress.completed_at = datetime.utcnow()

        db.session.commit()

        result = {
            'is_correct': is_correct,
            'correct_move': exercise.correct_move if not is_correct else None,
            'hint': exercise.hint if not is_correct else None,
            'explanation': exercise.explanation,
        }
        return result, 200

    @staticmethod
    def complete_lesson(user_id, lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'error': 'Урок не найден'}, 404

        progress = Progress.query.filter_by(
            user_id=user_id, lesson_id=lesson_id, exercise_id=None
        ).first()

        if not progress:
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                status='completed',
                completed_at=datetime.utcnow(),
            )
            db.session.add(progress)
        else:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()

        db.session.commit()
        return {'message': 'Урок завершён', 'progress': progress.to_dict()}, 200

    @staticmethod
    def get_topic_lessons(user_id, topic_id):
        from app.models.topic import Topic
        from app.models.lesson import Lesson
        from app.models.progress import Progress

        topic = Topic.query.get(topic_id)
        if not topic:
            return {'error': 'Тема не найдена'}, 404

        lessons = Lesson.query.filter_by(topic_id=topic_id).order_by(Lesson.order).all()

        completed_progress = Progress.query.filter_by(
            user_id=user_id, 
            status='completed',
            exercise_id=None
        ).all()
        completed_ids = {p.lesson_id for p in completed_progress}

        lessons_list = []
        for l in lessons:
            lesson_dict = l.to_dict()
            lesson_dict['is_completed'] = l.id in completed_ids
            lessons_list.append(lesson_dict)

        return {
            'topic_id': topic.id,
            'topic_title': getattr(topic, 'title', getattr(topic, 'name', '')),
            'lessons': lessons_list
        }, 200
