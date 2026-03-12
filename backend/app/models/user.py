from datetime import datetime

import bcrypt

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='student')  # student / admin
    age = db.Column(db.Integer)  # 5–12
    level = db.Column(db.String(30), default='beginner')  # beginner / intermediate / advanced
    elo_rating = db.Column(db.Integer, default=1200)
    avatar_url = db.Column(db.String(256))
    weak_topics = db.Column(db.JSON)  # [topic_id, ...] determined by test

    sms_code = db.Column(db.String(6))
    sms_code_expires = db.Column(db.DateTime)
    recovery_code = db.Column(db.String(6))
    recovery_code_expires = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    games_white = db.relationship('Game', foreign_keys='Game.white_id', backref='white_player', lazy='dynamic')
    games_black = db.relationship('Game', foreign_keys='Game.black_id', backref='black_player', lazy='dynamic')
    progress = db.relationship('Progress', backref='user', lazy='dynamic')
    test_attempts = db.relationship('TestAttempt', backref='user', lazy='dynamic')
    mistakes = db.relationship('Mistake', backref='user', lazy='dynamic')
    roadmaps = db.relationship('Roadmap', backref='user', lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8'),
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'age': self.age,
            'level': self.level,
            'elo_rating': self.elo_rating,
            'avatar_url': self.avatar_url,
            'weak_topics': self.weak_topics,
            'created_at': self.created_at.isoformat(),
        }
