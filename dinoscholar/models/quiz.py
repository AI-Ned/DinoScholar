from database import db
from datetime import datetime, timezone


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_type = db.Column(db.Text, nullable=False)  # module / daily / timed
    module_id = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)


class Achievement(db.Model):
    __tablename__ = "achievements"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    achievement_key = db.Column(db.Text, nullable=False)
    unlocked_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    __table_args__ = (db.UniqueConstraint("user_id", "achievement_key"),)
