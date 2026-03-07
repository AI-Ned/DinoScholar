from database import db
from datetime import datetime, timezone


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    lesson_progress = db.relationship("LessonProgress", backref="user", lazy=True)
    quiz_attempts = db.relationship("QuizAttempt", backref="user", lazy=True)
    achievements = db.relationship("Achievement", backref="user", lazy=True)
    study_sessions = db.relationship("StudySession", backref="user", lazy=True)
