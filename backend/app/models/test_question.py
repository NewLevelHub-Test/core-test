from app import db


class TestQuestion(db.Model):
    __tablename__ = 'test_questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    fen = db.Column(db.String(100))
    options = db.Column(db.JSON)  # ["e4", "d4", "Nf3", "c4"]
    correct_answer = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    # Добавь это в класс TestQuestion
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
# И связь, чтобы легко доставать имя темы
    topic = db.relationship('Topic', backref='question_items')

    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'question_text': self.question_text,
            'fen': self.fen,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'order': self.order,
            'topic_id': self.topic_id,
            'topic': self.topic.name if self.topic else None
        }
