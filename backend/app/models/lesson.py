from datetime import datetime

from app import db


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    theory_cards = db.Column(db.JSON)  # [{"title": "...", "text": "...", "image_url": "..."}]
    board_examples = db.Column(db.JSON)  # [{"fen": "...", "description": "...", "arrows": [...]}]
    difficulty = db.Column(db.String(20), default='beginner')
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'title': self.title,
            'content': self.content,
            'theory_cards': self.theory_cards,
            'board_examples': self.board_examples,
            'difficulty': self.difficulty,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
        }
