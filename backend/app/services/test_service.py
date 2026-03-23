from datetime import datetime

from app import db
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.test_attempt import TestAttempt
from app.models.topic import Topic
from app.models.user import User


LEVEL_THRESHOLDS = {
    'beginner': (0, 40),
    'intermediate': (41, 70),
    'advanced': (71, 100),
}


class TestService:

    @staticmethod
    def get_tests():
        tests = Test.query.all()
        return {'tests': [t.to_dict() for t in tests]}, 200

    @staticmethod
    def get_test(test_id):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404

        questions = TestQuestion.query.filter_by(
            test_id=test_id
        ).order_by(TestQuestion.order).all()

        q_list = []
        for q in questions:
            d = q.to_dict()
            del d['correct_answer']
            del d['explanation']
            q_list.append(d)

        return {
            'test': test.to_dict(),
            'questions': q_list,
        }, 200

    @staticmethod
    def start_test(user_id, test_id):
        test = Test.query.get(test_id)
        if not test:
            return {'error': 'Тест не найден'}, 404

        attempt = TestAttempt(
            user_id=user_id,
            test_id=test_id,
            total_questions=test.questions.count(),
        )
        db.session.add(attempt)
        db.session.commit()

        return {'attempt': attempt.to_dict()}, 201

    @staticmethod
    def submit_test(user_id, test_id, data):
        attempt = TestAttempt.query.filter_by(
            user_id=user_id, test_id=test_id, finished_at=None
        ).order_by(TestAttempt.started_at.desc()).first()

        if not attempt:
            return {'error': 'Активная попытка не найдена'}, 404

        if isinstance(data, list):
            answers_list = data
        elif isinstance(data, dict):
            answers_list = data.get('answers', data)
        else:
            answers_list = {}

        score = 0
        wrong_topics = []
        details = []
        saved_answers = {}

        if isinstance(answers_list, list):
            for item in answers_list:
                qid = item.get('question_id')
                user_answer = item.get('selected_option')
                if qid is None: continue
                
                question = TestQuestion.query.get(int(qid))
                if not question: continue

                is_correct = str(question.correct_answer) == str(user_answer)
                if is_correct:
                    score += 1
                else:
                    test_obj = Test.query.get(question.test_id)
                    if test_obj and test_obj.topic_id and test_obj.topic_id not in wrong_topics:
                        wrong_topics.append(test_obj.topic_id)

                saved_answers[str(qid)] = user_answer
                details.append({
                    'question_id': question.id,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'explanation': question.explanation,
                })
        else:
            for qid_str, user_answer in answers_list.items():
                question = TestQuestion.query.get(int(qid_str))
                if not question: continue

                is_correct = str(question.correct_answer) == str(user_answer)
                if is_correct:
                    score += 1
                else:
                    test_obj = Test.query.get(question.test_id)
                    if test_obj and test_obj.topic_id and test_obj.topic_id not in wrong_topics:
                        wrong_topics.append(test_obj.topic_id)

                saved_answers[qid_str] = user_answer
                details.append({
                    'question_id': question.id,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'explanation': question.explanation,
                })

        attempt.answers = saved_answers
        attempt.score = score
        attempt.finished_at = datetime.utcnow()

        percent = round(score / attempt.total_questions * 100) if attempt.total_questions else 0
        level = 'beginner'
        for lvl, (lo, hi) in LEVEL_THRESHOLDS.items():
            if lo <= percent <= hi:
                level = lvl
                break

        user = User.query.get(user_id)
        if user:
            user.level = level
            user.weak_topics = list(set((user.weak_topics or []) + wrong_topics))

        db.session.commit()

        return {
            'attempt': attempt.to_dict(),
            'details': details,
            'percent': percent,
            'level': level,
            'weak_topics': wrong_topics,
        }, 200

    @staticmethod
    def get_user_attempts(user_id):
        attempts = TestAttempt.query.filter_by(
            user_id=user_id
        ).order_by(TestAttempt.started_at.desc()).all()

        return {'attempts': [a.to_dict() for a in attempts]}, 200

    @staticmethod
    def get_attempt_detail(user_id, attempt_id):
        attempt = TestAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return {'error': 'Попытка не найдена'}, 404

        questions = TestQuestion.query.filter_by(test_id=attempt.test_id).order_by(TestQuestion.order).all()

        details = []
        answers = attempt.answers or {}
        for q in questions:
            user_answer = answers.get(str(q.id))
            details.append({
                'question': q.to_dict(),
                'user_answer': user_answer,
                'is_correct': user_answer == q.correct_answer if user_answer else False,
            })

        return {
            'attempt': attempt.to_dict(),
            'details': details,
        }, 200

    @staticmethod
    def get_level_info(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        weak = []
        if user.weak_topics:
            topics = Topic.query.filter(Topic.id.in_(user.weak_topics)).all()
            weak = [t.to_dict() for t in topics]

        return {
            'level': user.level,
            'elo_rating': user.elo_rating,
            'weak_topics': weak,
        }, 200
