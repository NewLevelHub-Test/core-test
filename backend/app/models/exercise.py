from app import db


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    fen = db.Column(db.String(100), nullable=False)
    correct_move = db.Column(db.String(10), nullable=False)
    hint = db.Column(db.Text)
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='beginner')
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'fen': self.fen,
            'correct_move': self.correct_move,
            'hint': self.hint,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'order': self.order,
        }
