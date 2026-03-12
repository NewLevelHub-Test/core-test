from datetime import datetime

from app import db


class Mistake(db.Model):
    __tablename__ = 'mistakes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    fen = db.Column(db.String(100))
    move_played = db.Column(db.String(10))
    best_move = db.Column(db.String(10))
    explanation = db.Column(db.Text)  # simple language explanation for kids
    category = db.Column(db.String(50))  # tactic / opening / endgame / positional
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    evaluation_loss = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'fen': self.fen,
            'move_played': self.move_played,
            'best_move': self.best_move,
            'explanation': self.explanation,
            'category': self.category,
            'topic_id': self.topic_id,
            'evaluation_loss': self.evaluation_loss,
            'created_at': self.created_at.isoformat(),
        }
