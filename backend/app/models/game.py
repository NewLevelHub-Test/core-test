from datetime import datetime

from app import db


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    white_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    black_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pgn = db.Column(db.Text)
    fen = db.Column(db.String(100), default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    status = db.Column(db.String(20), default='in_progress')  # in_progress / finished / draw
    result = db.Column(db.String(10))  # 1-0 / 0-1 / 1/2-1/2
    mode = db.Column(db.String(20), default='ai')  # pvp / ai
    bot_level = db.Column(db.Integer, default=5)  # 1–20 stockfish skill
    player_color = db.Column(db.String(5), default='white')  # white / black
    time_control = db.Column(db.Integer)  # seconds, nullable = unlimited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

    moves = db.relationship('Move', backref='game', lazy='dynamic', order_by='Move.move_number')

    @property
    def difficulty(self):
        if self.bot_level is None:
            return None
        if self.bot_level <= 5:
            return 1
        elif self.bot_level <= 14:
            return 2
        else:
            return 3

    @property
    def result_text(self):
        mapping = {'1-0': 'win', '0-1': 'loss', '1/2-1/2': 'draw'}
        if self.result in mapping:
            if self.player_color == 'black':
                rev = {'win': 'loss', 'loss': 'win', 'draw': 'draw'}
                return rev[mapping[self.result]]
            return mapping[self.result]
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'white_id': self.white_id,
            'black_id': self.black_id,
            'pgn': self.pgn,
            'fen': self.fen,
            'status': self.status,
            'result': self.result,
            'result_text': self.result_text,
            'mode': self.mode,
            'bot_level': self.bot_level,
            'difficulty': self.difficulty,
            'player_color': self.player_color,
            'time_control': self.time_control,
            'created_at': self.created_at.isoformat(),
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
        }
