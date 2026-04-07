import random
from app import db
from app.models.roadmap import Roadmap
from app.models.roadmap_week import RoadmapWeek
from app.models.daily_task import DailyTask
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.user import User
from datetime import datetime

WEEK_TEMPLATES = [
    [
        {'day': 1, 'type': 'lesson', 'title': 'Введение в тему'},
        {'day': 2, 'type': 'exercise', 'title': 'Закрепление основ'},
        {'day': 3, 'type': 'lesson', 'title': 'Углубленное изучение'},
        {'day': 4, 'type': 'exercise', 'title': 'Практика на мат'},
        {'day': 5, 'type': 'game', 'title': 'Партия с ботом'},
        {'day': 6, 'type': 'exercise', 'title': 'Поиск ошибок'},
        {'day': 7, 'type': 'test', 'title': 'Тест недели'},
    ],

    [
        {'day': 1, 'type': 'lesson', 'title': 'Краткий обзор'},
        {'day': 2, 'type': 'exercise', 'title': 'Тактический тренажер'},
        {'day': 3, 'type': 'exercise', 'title': 'Решение этюдов'},
        {'day': 4, 'type': 'game', 'title': 'Тренировочный матч'},
        {'day': 5, 'type': 'lesson', 'title': 'Разбор стратегий'},
        {'day': 6, 'type': 'game', 'title': 'Реванш с ботом'},
        {'day': 7, 'type': 'test', 'title': 'Проверка навыков'},
    ],

    [
        {'day': 1, 'type': 'lesson', 'title': 'Теория и примеры'},
        {'day': 2, 'type': 'game', 'title': 'Легкая разминка'},
        {'day': 3, 'type': 'exercise', 'title': 'Задачи на время'},
        {'day': 4, 'type': 'lesson', 'title': 'Мастер-класс'},
        {'day': 5, 'type': 'game', 'title': 'Серьезная игра'},
        {'day': 6, 'type': 'exercise', 'title': 'Анализ позиции'},
        {'day': 7, 'type': 'test', 'title': 'Экзамен'},
    ]
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
        user = db.session.get(User, user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        level = level or user.level or 'beginner'

        existing = Roadmap.query.filter_by(user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.flush()

        all_topics = Topic.query.order_by(Topic.order).all()
        user_weak_ids = user.weak_topics if user.weak_topics else []
        
        weak_topics = [t for t in all_topics if t.id in user_weak_ids]
        other_topics = [t for t in all_topics if t.id not in user_weak_ids]
        sorted_topics = weak_topics + other_topics

        roadmap = Roadmap(
            user_id=user_id,
            level=level,
            total_weeks=len(sorted_topics),
            current_week=1,
            title=f'План обучения: {level.capitalize()}'
        )
        db.session.add(roadmap)
        db.session.flush()

        for i, topic in enumerate(sorted_topics, start=1):
            is_weak = topic.id in user_weak_ids
            
            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=i,
                title=f'Неделя {i}: {topic.name}',
                description=f'{"[ПРИОРИТЕТ] " if is_weak else ""}Изучаем: {topic.description}',
                topics=[topic.id],
            )
            db.session.add(week)
            db.session.flush()

            lessons = Lesson.query.filter_by(topic_id=topic.id).order_by(Lesson.order).all()
            
            template = random.choice(WEEK_TEMPLATES)

            for tmpl in template:
                ref_id = None
                if tmpl['type'] == 'lesson' and lessons:
                    lesson_idx = (tmpl['day'] // 2) % len(lessons)
                    ref_id = lessons[lesson_idx].id

                task = DailyTask(
                    week_id=week.id,
                    day_number=tmpl['day'],
                    task_type=tmpl['type'],
                    title=tmpl['title'],
                    description=f'{topic.name}: {tmpl["title"]}',
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
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        return {'week': week.to_dict()}, 200

    @staticmethod
    def complete_week(user_id, week_id):
        week = RoadmapWeek.query.get(week_id)
        if not week:
            return {'error': 'Неделя не найдена'}, 404

        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        week.is_completed = True

        if roadmap.current_week == week.week_number:
            roadmap.current_week = min(week.week_number + 1, roadmap.total_weeks)

        db.session.commit()
        return {'week': week.to_dict()}, 200

    @staticmethod
    def complete_daily_task(user_id, task_id):
        from app.models.progress import Progress
        
        task = DailyTask.query.get(task_id)
        if not task:
            return {'error': 'Задание не найдено'}, 404

        week = RoadmapWeek.query.get(task.week_id)
        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        # 1. МЕНЯЕМ СТАТУС (Toggle)
        task.is_completed = not task.is_completed

        # 2. ОБНОВЛЯЕМ ТАБЛИЦУ PROGRESS
        if task.reference_id:
            # Ищем существующую запись
            existing_progress = Progress.query.filter_by(
                user_id=user_id,
                lesson_id=task.reference_id if task.task_type == 'lesson' else None,
                exercise_id=task.reference_id if task.task_type == 'exercise' else None
            ).first()

            if task.is_completed:
                # Если поставили галочку
                if not existing_progress:
                    new_progress = Progress(
                        user_id=user_id,
                        lesson_id=task.reference_id if task.task_type == 'lesson' else None,
                        exercise_id=task.reference_id if task.task_type == 'exercise' else None,
                        status='completed',
                        completed_at=datetime.utcnow()
                    )
                    db.session.add(new_progress)
                else:
                    existing_progress.status = 'completed'
                    existing_progress.completed_at = datetime.utcnow()
            else:
                # Если УБРАЛИ галочку
                if existing_progress:
                    existing_progress.status = 'in_progress'
                    existing_progress.completed_at = None

        # 3. ПРОВЕРКА ЗАВЕРШЕННОСТИ НЕДЕЛИ
        all_done = not DailyTask.query.filter_by(
            week_id=week.id, is_completed=False
        ).first()
        
        week.is_completed = all_done
        
        # Обновляем текущую неделю роадмапа, если нужно
        if all_done and roadmap.current_week == week.week_number:
            roadmap.current_week = min(week.week_number + 1, roadmap.total_weeks)

        db.session.commit()

        # 4. СЧИТАЕМ НОВЫЙ ПРОЦЕНТ ДЛЯ ОТВЕТА
        total_tasks = DailyTask.query.join(RoadmapWeek).filter(RoadmapWeek.roadmap_id == roadmap.id).count()
        completed_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id, 
            DailyTask.is_completed == True
        ).count()
        
        new_percent = round(completed_tasks / total_tasks * 100) if total_tasks else 0

        return {
            'task': task.to_dict(), 
            'week_completed': all_done,
            'roadmap_progress': new_percent # Отправляем новый процент фронтенду
        }, 200

        

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
