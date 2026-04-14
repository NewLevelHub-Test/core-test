from app import db


class DailyTask(db.Model):
    __tablename__ = 'daily_tasks'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('roadmap_weeks.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    task_type = db.Column(db.String(30), nullable=False)  # lesson / exercise / test
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    reference_id = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)

    lesson_content = db.Column(db.JSON)
    quiz_questions = db.Column(db.JSON)
    quiz_passed = db.Column(db.Boolean, default=False)
    quiz_score = db.Column(db.Integer)
    content_generated = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'week_id': self.week_id,
            'day_number': self.day_number,
            'task_type': self.task_type,
            'title': self.title,
            'description': self.description,
            'reference_id': self.reference_id,
            'is_completed': self.is_completed,
            'quiz_passed': self.quiz_passed,
            'quiz_score': self.quiz_score,
            'content_generated': self.content_generated or False,
            'has_content': self.content_generated or False,
        }

    def to_dict_full(self):
        data = self.to_dict()
        data['lesson_content'] = self.lesson_content
        data['quiz_questions'] = self._safe_quiz()
        return data

    def _safe_quiz(self):
        if not self.quiz_questions:
            return []
        return [
            {
                'question': q.get('question', ''),
                'options': q.get('options', []),
            }
            for q in self.quiz_questions
        ]
