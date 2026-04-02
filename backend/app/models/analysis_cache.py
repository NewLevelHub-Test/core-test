from app import db
from datetime import datetime

class AnalysisCache(db.Model):
    __tablename__ = 'analysis_cache'

    id = db.Column(db.Integer, primary_key=True)
    fen = db.Column(db.String(100), unique=True, nullable=False, index=True)
    evaluation = db.Column(db.Float)
    best_move = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)