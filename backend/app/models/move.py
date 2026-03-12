from app import db


class Move(db.Model):
    __tablename__ = 'moves'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    notation = db.Column(db.String(10), nullable=False)  # SAN, e.g. "e4", "Nf3"
    fen_after = db.Column(db.String(100))
    evaluation = db.Column(db.Float)
    is_blunder = db.Column(db.Boolean, default=False)
    is_mistake = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(5))  # white / black

    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'move_number': self.move_number,
            'notation': self.notation,
            'fen_after': self.fen_after,
            'evaluation': self.evaluation,
            'is_blunder': self.is_blunder,
            'is_mistake': self.is_mistake,
            'color': self.color,
        }
