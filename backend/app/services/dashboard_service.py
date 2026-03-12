from app.models.user import User
from app.models.game import Game
from app.models.progress import Progress
from app.models.test_attempt import TestAttempt
from app.models.roadmap import Roadmap
from app.models.roadmap_week import RoadmapWeek
from app.models.daily_task import DailyTask
from app.models.lesson import Lesson


class DashboardService:

    @staticmethod
    def get_dashboard(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        recent_games = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).order_by(Game.created_at.desc()).limit(5).all()

        lesson_progress = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).count()

        last_test = TestAttempt.query.filter_by(
            user_id=user_id
        ).order_by(TestAttempt.started_at.desc()).first()

        roadmap = Roadmap.query.filter_by(user_id=user_id).first()

        roadmap_widget = None
        if roadmap:
            current = RoadmapWeek.query.filter_by(
                roadmap_id=roadmap.id, week_number=roadmap.current_week
            ).first()
            total_completed = RoadmapWeek.query.filter_by(
                roadmap_id=roadmap.id, is_completed=True
            ).count()
            roadmap_widget = {
                'roadmap': roadmap.to_dict(),
                'current_week': current.to_dict() if current else None,
                'weeks_completed': total_completed,
                'progress_percent': round(total_completed / roadmap.total_weeks * 100) if roadmap.total_weeks else 0,
            }

        recommendation, _ = DashboardService.get_recommendation(user_id)

        return {
            'user': user.to_dict(),
            'recommendation': recommendation.get('recommendation'),
            'roadmap_widget': roadmap_widget,
            'recent_games': [g.to_dict() for g in recent_games],
            'completed_lessons': lesson_progress,
            'last_test': last_test.to_dict() if last_test else None,
            'quick_actions': [
                {'key': 'test', 'label': 'Пройти тест', 'url': '/api/tests'},
                {'key': 'lessons', 'label': 'Уроки', 'url': '/api/lessons'},
                {'key': 'game', 'label': 'Игра с ботом', 'url': '/api/games'},
                {'key': 'history', 'label': 'История', 'url': '/api/games/history'},
                {'key': 'photo', 'label': 'Загрузить фото', 'url': '/api/photo/recognize'},
            ],
        }, 200

    @staticmethod
    def get_recommendation(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        has_test = TestAttempt.query.filter_by(user_id=user_id).first()
        if not has_test:
            return {'recommendation': {
                'action': 'test',
                'title': 'Пройди тест на определение уровня',
                'description': 'Мы подберём для тебя программу обучения',
            }}, 200

        roadmap = Roadmap.query.filter_by(user_id=user_id).first()
        if roadmap:
            current_week = RoadmapWeek.query.filter_by(
                roadmap_id=roadmap.id, week_number=roadmap.current_week
            ).first()
            if current_week:
                pending_task = DailyTask.query.filter_by(
                    week_id=current_week.id, is_completed=False
                ).order_by(DailyTask.day_number).first()
                if pending_task:
                    return {'recommendation': {
                        'action': pending_task.task_type,
                        'title': pending_task.title,
                        'description': pending_task.description or 'Выполни задание дня',
                        'task_id': pending_task.id,
                        'reference_id': pending_task.reference_id,
                    }}, 200

        last_lesson = Progress.query.filter_by(
            user_id=user_id, status='completed'
        ).filter(Progress.lesson_id.isnot(None)).order_by(Progress.completed_at.desc()).first()

        if last_lesson:
            next_lesson = Lesson.query.filter(
                Lesson.topic_id == Lesson.query.get(last_lesson.lesson_id).topic_id if last_lesson.lesson_id else True,
                Lesson.order > (Lesson.query.get(last_lesson.lesson_id).order if last_lesson.lesson_id else 0)
            ).order_by(Lesson.order).first()
            if next_lesson:
                return {'recommendation': {
                    'action': 'lesson',
                    'title': f'Продолжи: {next_lesson.title}',
                    'description': 'Следующий урок ждёт тебя',
                    'reference_id': next_lesson.id,
                }}, 200

        return {'recommendation': {
            'action': 'game',
            'title': 'Сыграй партию с ботом',
            'description': 'Практика — лучший способ научиться!',
        }}, 200

    @staticmethod
    def get_activity(user_id):
        games = Game.query.filter(
            (Game.white_id == user_id) | (Game.black_id == user_id)
        ).order_by(Game.created_at.desc()).limit(20).all()

        return {
            'activity': [g.to_dict() for g in games],
        }, 200
