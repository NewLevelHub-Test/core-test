from datetime import datetime

from app import db


class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    difficulty = db.Column(db.String(20), default='beginner')
    time_limit = db.Column(db.Integer)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('TestQuestion', backref='test', lazy='dynamic')
    attempts = db.relationship('TestAttempt', backref='test', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'topic_id': self.topic_id,
            'difficulty': self.difficulty,
            'time_limit': self.time_limit,
            'created_at': self.created_at.isoformat(),
        }
