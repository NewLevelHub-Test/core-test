from datetime import datetime

from app import db


class Roadmap(db.Model):
    __tablename__ = 'roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='Персональный план обучения')
    level = db.Column(db.String(20))
    total_weeks = db.Column(db.Integer, default=52)  # year-based plan
    current_week = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    weeks = db.relationship('RoadmapWeek', backref='roadmap', lazy='dynamic',
                            order_by='RoadmapWeek.week_number', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'level': self.level,
            'total_weeks': self.total_weeks,
            'current_week': self.current_week,
            'created_at': self.created_at.isoformat(),
        }
