from app import db
from app.models.roadmap import Roadmap
from app.models.roadmap_week import RoadmapWeek
from app.models.daily_task import DailyTask
from app.models.user import User
from app.services.roadmap_ai_service import (
    get_curriculum,
    WEEK_TASK_TEMPLATE,
    generate_task_content,
)
from datetime import datetime

TOTAL_WEEKS = 12


def _int_id(user_id):
    try:
        return int(user_id)
    except (TypeError, ValueError):
        return None


class RoadmapService:

    @staticmethod
    def get_roadmap(user_id):
        user_id = _int_id(user_id)
        roadmap = Roadmap.query.filter_by(user_id=user_id).first()
        if not roadmap:
            return {'error': 'План обучения не создан. Пройдите тест для генерации'}, 404

        weeks = roadmap.weeks.all()

        weeks_data = []
        for w in weeks:
            wd = w.to_dict()
            prev_done = True
            if w.week_number > 1:
                prev = RoadmapWeek.query.filter_by(
                    roadmap_id=roadmap.id,
                    week_number=w.week_number - 1,
                ).first()
                prev_done = prev.is_completed if prev else True
            wd['is_locked'] = not prev_done and w.week_number > 1
            weeks_data.append(wd)

        return {
            'roadmap': roadmap.to_dict(),
            'weeks': weeks_data,
        }, 200

    @staticmethod
    def generate_roadmap(user_id, level=None):
        user_id = _int_id(user_id)
        user = db.session.get(User, user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        level = level or user.level or 'beginner'

        existing = Roadmap.query.filter_by(user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.flush()

        curriculum = get_curriculum(level)

        roadmap = Roadmap(
            user_id=user_id,
            level=level,
            total_weeks=TOTAL_WEEKS,
            current_week=1,
            title=f'План обучения: {level.capitalize()}',
        )
        db.session.add(roadmap)
        db.session.flush()

        for i, topic_info in enumerate(curriculum[:TOTAL_WEEKS], start=1):
            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=i,
                title=f'Неделя {i}: {topic_info["topic"]}',
                description=topic_info['desc'],
                topics=[],
            )
            db.session.add(week)
            db.session.flush()

            for tmpl in WEEK_TASK_TEMPLATE:
                task = DailyTask(
                    week_id=week.id,
                    day_number=tmpl['day'],
                    task_type=tmpl['type'],
                    title=f'{topic_info["topic"]}: {tmpl["suffix"]}',
                    description=f'{topic_info["desc"]} — {tmpl["suffix"]}',
                    content_generated=False,
                )
                db.session.add(task)

        db.session.commit()

        return {
            'roadmap': roadmap.to_dict(),
            'weeks': [w.to_dict() for w in roadmap.weeks.all()],
        }, 201

    @staticmethod
    def get_task_content(user_id, task_id):
        user_id = _int_id(user_id)
        task = DailyTask.query.get(task_id)
        if not task:
            return {'error': 'Задание не найдено'}, 404

        week = RoadmapWeek.query.get(task.week_id)
        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        if week.week_number > 1:
            prev = RoadmapWeek.query.filter_by(
                roadmap_id=roadmap.id,
                week_number=week.week_number - 1,
            ).first()
            if prev and not prev.is_completed:
                return {'error': 'Сначала завершите предыдущую неделю'}, 403

        if not task.content_generated:
            topic_name = week.title.replace(f'Неделя {week.week_number}: ', '')
            content = generate_task_content(
                topic_name=topic_name,
                task_title=task.title,
                task_type=task.task_type,
                level=roadmap.level or 'beginner',
                week_description=week.description or '',
            )
            task.lesson_content = content.get('steps', [])
            task.quiz_questions = content.get('quiz', [])
            task.content_generated = True
            db.session.commit()

        return {'task': task.to_dict_full()}, 200

    @staticmethod
    def submit_task_quiz(user_id, task_id, answers):
        from app.models.progress import Progress
        user_id = _int_id(user_id)

        task = DailyTask.query.get(task_id)
        if not task:
            return {'error': 'Задание не найдено'}, 404

        week = RoadmapWeek.query.get(task.week_id)
        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        if task.is_completed:
            return {'error': 'Задание уже завершено'}, 400

        if not task.quiz_questions:
            return {'error': 'У задания нет теста'}, 400

        quiz = task.quiz_questions
        total = len(quiz)
        correct = 0

        results = []
        for i, q in enumerate(quiz):
            user_answer = answers[i] if i < len(answers) else -1
            is_correct = user_answer == q.get('correct', -1)
            if is_correct:
                correct += 1
            results.append({
                'question': q.get('question', ''),
                'user_answer': user_answer,
                'correct_answer': q.get('correct', 0),
                'is_correct': is_correct,
                'explanation': q.get('explanation', ''),
            })

        score = round(correct / total * 100) if total > 0 else 0
        passed = score >= 60

        task.quiz_score = score
        task.quiz_passed = passed

        if passed:
            task.is_completed = True

            if task.reference_id and task.task_type in ('lesson', 'exercise'):
                existing = Progress.query.filter_by(
                    user_id=user_id,
                    lesson_id=task.reference_id if task.task_type == 'lesson' else None,
                    exercise_id=task.reference_id if task.task_type == 'exercise' else None,
                ).first()
                if not existing:
                    new_progress = Progress(
                        user_id=user_id,
                        lesson_id=task.reference_id if task.task_type == 'lesson' else None,
                        exercise_id=task.reference_id if task.task_type == 'exercise' else None,
                        status='completed',
                        completed_at=datetime.utcnow(),
                    )
                    db.session.add(new_progress)

            all_done = not DailyTask.query.filter_by(
                week_id=week.id, is_completed=False,
            ).filter(DailyTask.id != task.id).first()

            if all_done:
                week.is_completed = True
                if roadmap.current_week == week.week_number:
                    roadmap.current_week = min(week.week_number + 1, roadmap.total_weeks)

        db.session.commit()

        total_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id,
        ).count()
        completed_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id,
            DailyTask.is_completed == True,
        ).count()
        new_percent = round(completed_tasks / total_tasks * 100) if total_tasks else 0

        return {
            'passed': passed,
            'score': score,
            'correct': correct,
            'total': total,
            'results': results,
            'task': task.to_dict(),
            'week_completed': week.is_completed,
            'roadmap_progress': new_percent,
        }, 200

    @staticmethod
    def complete_daily_task(user_id, task_id):
        """Legacy toggle — kept for backward compat but now requires quiz."""
        user_id = _int_id(user_id)
        task = DailyTask.query.get(task_id)
        if not task:
            return {'error': 'Задание не найдено'}, 404

        week = RoadmapWeek.query.get(task.week_id)
        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        if not task.quiz_passed and not task.is_completed:
            return {'error': 'Сначала пройдите тест по уроку'}, 400

        return {'task': task.to_dict()}, 200

    @staticmethod
    def get_week_detail(user_id, week_id):
        user_id = _int_id(user_id)
        week = RoadmapWeek.query.get(week_id)
        if not week:
            return {'error': 'Неделя не найдена'}, 404

        roadmap = Roadmap.query.get(week.roadmap_id)
        if int(roadmap.user_id) != int(user_id):
            return {'error': 'Доступ запрещён'}, 403

        return {'week': week.to_dict()}, 200

    @staticmethod
    def complete_week(user_id, week_id):
        user_id = _int_id(user_id)
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
    def get_progress(user_id):
        user_id = _int_id(user_id)
        roadmap = Roadmap.query.filter_by(user_id=user_id).first()
        if not roadmap:
            return {'error': 'План обучения не найден'}, 404

        weeks = roadmap.weeks.all()
        completed_weeks = sum(1 for w in weeks if w.is_completed)
        total_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id,
        ).count()
        completed_tasks = DailyTask.query.join(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == roadmap.id,
            DailyTask.is_completed == True,
        ).count()

        return {
            'total_weeks': roadmap.total_weeks,
            'completed_weeks': completed_weeks,
            'current_week': roadmap.current_week,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_percent': round(completed_tasks / total_tasks * 100) if total_tasks else 0,
        }, 200
