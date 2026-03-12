from app import db


class DailyTask(db.Model):
    __tablename__ = 'daily_tasks'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('roadmap_weeks.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)  # 1–7
    task_type = db.Column(db.String(30), nullable=False)  # lesson / exercise / game / test
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    reference_id = db.Column(db.Integer)  # lesson_id / exercise_id / test_id
    is_completed = db.Column(db.Boolean, default=False)

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
        }
