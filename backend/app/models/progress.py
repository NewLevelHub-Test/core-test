from datetime import datetime

from app import db


class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'))
    status = db.Column(db.String(20), default='not_started')  # not_started / in_progress / completed
    score = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'exercise_id': self.exercise_id,
            'status': self.status,
            'score': self.score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
        }
