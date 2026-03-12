from app import db
from app.models.roadmap import Roadmap
from app.models.roadmap_week import RoadmapWeek
from app.models.daily_task import DailyTask
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.user import User


DAYS_PER_WEEK = 7

DAILY_TEMPLATE = [
    {'day': 1, 'type': 'lesson', 'title': 'Изучи новую тему'},
    {'day': 2, 'type': 'exercise', 'title': 'Реши задачи по теме'},
    {'day': 3, 'type': 'lesson', 'title': 'Продолжи урок'},
    {'day': 4, 'type': 'exercise', 'title': 'Практика: задачи'},
    {'day': 5, 'type': 'game', 'title': 'Сыграй партию с ботом'},
    {'day': 6, 'type': 'exercise', 'title': 'Повторение и задачи'},
    {'day': 7, 'type': 'test', 'title': 'Мини-тест недели'},
]


class RoadmapService:

    @staticmethod
    def get_roadmap(user_id):
        roadmap = Roadmap.query.filter_by(user_id=user_id).first()
        if not roadmap:
            return {'error': 'План обучения не создан. Пройдите тест для генерации'}, 404

        weeks = roadmap.weeks.all()
        return {
            'roadmap': roadmap.to_dict(),
            'weeks': [w.to_dict() for w in weeks],
        }, 200

    @staticmethod
    def generate_roadmap(user_id, level=None):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        if not level:
            level = user.level or 'beginner'

        existing = Roadmap.query.filter_by(user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.flush()

        topics = Topic.query.order_by(Topic.order).all()
        total_weeks = max(len(topics), 12)

        roadmap = Roadmap(
            user_id=user_id,
            level=level,
            total_weeks=total_weeks,
            current_week=1,
        )
        db.session.add(roadmap)
        db.session.flush()

        for i, topic in enumerate(topics, start=1):
            lessons = Lesson.query.filter_by(topic_id=topic.id).order_by(Lesson.order).all()

            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=i,
                title=f'Неделя {i}: {topic.name}',
                description=topic.description,
                topics=[topic.id],
            )
            db.session.add(week)
            db.session.flush()

            for tmpl in DAILY_TEMPLATE:
                ref_id = None
                if tmpl['type'] == 'lesson' and lessons:
                    idx = min(tmpl['day'] // 2, len(lessons) - 1)
                    ref_id = lessons[idx].id

                task = DailyTask(
                    week_id=week.id,
                    day_number=tmpl['day'],
                    task_type=tmpl['type'],
                    title=tmpl['title'],
                    description=f'{topic.name} — {tmpl["title"]}',
                    reference_id=ref_id,
                )
                db.session.add(task)

        db.session.commit()

        return {
            'roadmap': roadmap.to_dict(),
            'weeks': [w.to_dict() for w in roadmap.weeks.all()],
        }, 201

    @staticmethod
    def get_week_detail(user_id, week_id):
        week = RoadmapWeek.query.get(week_id)
        if not week:
            return {'error': 'Неделя не найдена'}, 404

        roadmap = Roadmap.query.get(week.roadmap_id)
        if roadmap.user_id != user_id:
            return {'error': 'Доступ запрещён'}, 403

        return {'week': week.to_dict()}, 200

    @staticmethod
    def complete_week(user_id, week_id):
        week = RoadmapWeek.query.get(week_id)
        if not week:
            return {'error': 'Неделя не найдена'}, 404

        roadmap = Roadmap.query.get(week.roadmap_id)
        if roadmap.user_id != user_id:
            return {'error': 'Доступ запрещён'}, 403

        week.is_completed = True

        if roadmap.current_week == week.week_number:
            roadmap.current_week = min(week.week_number + 1, roadmap.total_weeks)

        db.session.commit()
        return {'week': week.to_dict()}, 200

    @staticmethod
    def complete_daily_task(user_id, task_id):
        task = DailyTask.query.get(task_id)
        if not task:
            return {'error': 'Задание не найдено'}, 404

        week = RoadmapWeek.query.get(task.week_id)
        roadmap = Roadmap.query.get(week.roadmap_id)
        if roadmap.user_id != user_id:
            return {'error': 'Доступ запрещён'}, 403

        task.is_completed = True

        all_done = not DailyTask.query.filter_by(
            week_id=week.id, is_completed=False
        ).first()
        if all_done:
            week.is_completed = True
            if roadmap.current_week == week.week_number:
                roadmap.current_week = min(week.week_number + 1, roadmap.total_weeks)

        db.session.commit()
        return {'task': task.to_dict(), 'week_completed': all_done}, 200

    @staticmethod
    def get_progress(user_id):
        roadmap = Roadmap.query.filter_by(user_id=user_id).first()
        if not roadmap:
            return {'error': 'План обучения не найден'}, 404

        weeks = roadmap.weeks.all()
        completed_weeks = sum(1 for w in weeks if w.is_completed)
        total_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id
        ).count()
        completed_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id,
            DailyTask.is_completed == True
        ).count()

        return {
            'total_weeks': roadmap.total_weeks,
            'completed_weeks': completed_weeks,
            'current_week': roadmap.current_week,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_percent': round(completed_tasks / total_tasks * 100) if total_tasks else 0,
        }, 200
