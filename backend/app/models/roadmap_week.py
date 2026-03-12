from app import db


class RoadmapWeek(db.Model):
    __tablename__ = 'roadmap_weeks'

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    topics = db.Column(db.JSON)  # [topic_id, ...]
    is_completed = db.Column(db.Boolean, default=False)

    daily_tasks = db.relationship('DailyTask', backref='week', lazy='dynamic',
                                  order_by='DailyTask.day_number', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'roadmap_id': self.roadmap_id,
            'week_number': self.week_number,
            'title': self.title,
            'description': self.description,
            'topics': self.topics,
            'is_completed': self.is_completed,
            'daily_tasks': [t.to_dict() for t in self.daily_tasks.all()],
        }
