import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models.user import User
from app.models.game import Game
from app.models.progress import Progress
from app.models.test_attempt import TestAttempt


class UserService:

    @staticmethod
    def get_profile(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404
        return {'user': user.to_dict()}, 200

    @staticmethod
    def update_profile(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return {'error': 'Имя пользователя занято'}, 409
            user.username = data['username']

        if 'email' in data:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return {'error': 'Email уже используется'}, 409
            user.email = data['email']

        if 'age' in data:
            age = data['age']
            if not isinstance(age, int) or age < 5 or age > 12:
                return {'error': 'Возраст должен быть от 5 до 12'}, 400
            user.age = age

        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        return {'user': user.to_dict()}, 200

    @staticmethod
    def upload_avatar(user_id, file):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in {'png', 'jpg', 'jpeg'}:
            return {'error': 'Недопустимый формат'}, 400

        filename = f'avatar_{user_id}_{uuid.uuid4().hex}.{ext}'
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        user.avatar_url = filename
        db.session.commit()

        return {'avatar_url': filename}, 200

    @staticmethod
    def get_stats(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        total_games = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).count()

        wins = Game.query.filter(
            ((Game.white_id == user_id) & (Game.result == '1-0')) |
            ((Game.black_id == user_id) & (Game.result == '0-1'))
        ).count()

        completed_lessons = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).filter(Progress.lesson_id.isnot(None)).count()

        test_count = TestAttempt.query.filter_by(user_id=user_id).count()

        return {
            'elo_rating': user.elo_rating,
            'level': user.level,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'completed_lessons': completed_lessons,
            'tests_taken': test_count,
        }, 200

    @staticmethod
    def get_learning_progress(user_id, page=1):
        pagination = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).order_by(Progress.completed_at.desc()).paginate(
            page=page, per_page=15, error_out=False
        )

        return {
            'progress': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }, 200

    @staticmethod
    def get_activity_history(user_id, page=1):
        pagination = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).order_by(Progress.completed_at.desc()).paginate(
            page=page, per_page=15, error_out=False
        )

        return {
            'progress': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }, 200

        tests = TestAttempt.query.filter_by(
            user_id=user_id
        ).order_by(TestAttempt.started_at.desc()).limit(5).all()

        return {
            'games': [g.to_dict() for g in pagination.items],
            'total_games': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'recent_tests': [t.to_dict() for t in tests],
        }, 200
