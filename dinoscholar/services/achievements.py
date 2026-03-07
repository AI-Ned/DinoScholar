import json
import os
from datetime import datetime, date, timezone, timedelta

from database import db
from models.quiz import Achievement, QuizAttempt
from models.progress import LessonProgress, StudySession


class AchievementService:
    def __init__(self, data_path: str):
        self._catalogue: list[dict] = []
        self._load_catalogue(data_path)

    def _load_catalogue(self, data_path: str) -> None:
        filepath = os.path.join(data_path, "achievements.json")
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            self._catalogue = json.load(f)

    def get_catalogue(self) -> list[dict]:
        return list(self._catalogue)

    def check_and_award(self, user_id: int, event: str, context: dict) -> list[str]:
        newly_unlocked = []

        if event == "lesson_completed":
            newly_unlocked.extend(self._check_lesson_achievements(user_id, context))
        elif event == "quiz_submitted":
            newly_unlocked.extend(self._check_quiz_achievements(user_id, context))
        elif event == "species_viewed":
            newly_unlocked.extend(self._check_species_achievements(user_id, context))
        elif event == "session_ended":
            newly_unlocked.extend(self._check_study_achievements(user_id))

        return newly_unlocked

    def _award(self, user_id: int, key: str) -> bool:
        existing = Achievement.query.filter_by(
            user_id=user_id, achievement_key=key
        ).first()
        if existing:
            return False
        achievement = Achievement(
            user_id=user_id,
            achievement_key=key,
            unlocked_at=datetime.now(timezone.utc),
        )
        db.session.add(achievement)
        db.session.commit()
        return True

    def _check_lesson_achievements(self, user_id: int, context: dict) -> list[str]:
        unlocked = []
        # First lesson
        count = LessonProgress.query.filter_by(user_id=user_id, completed=True).count()
        if count >= 1 and self._award(user_id, "first_lesson"):
            unlocked.append("first_lesson")

        # Module complete
        module_id = context.get("module_id")
        if module_id:
            total_in_module = context.get("total_lessons", 0)
            completed_in_module = LessonProgress.query.filter_by(
                user_id=user_id, module_id=module_id, completed=True
            ).count()
            if total_in_module > 0 and completed_in_module >= total_in_module:
                key = f"module_complete_{module_id}"
                if self._award(user_id, key):
                    unlocked.append(key)

        # All modules
        total_modules_complete = 0
        for i in range(1, 9):
            mid = f"module_{i:02d}"
            total = context.get(f"module_{mid}_total", 0)
            done = LessonProgress.query.filter_by(
                user_id=user_id, module_id=mid, completed=True
            ).count()
            if total > 0 and done >= total:
                total_modules_complete += 1
        if total_modules_complete >= 8 and self._award(user_id, "all_modules"):
            unlocked.append("all_modules")

        return unlocked

    def _check_quiz_achievements(self, user_id: int, context: dict) -> list[str]:
        unlocked = []
        score = context.get("score", 0)
        total = context.get("total", 0)
        difficulty = context.get("difficulty", "")

        if total > 0 and score == total:
            if self._award(user_id, "quiz_perfect"):
                unlocked.append("quiz_perfect")
            if difficulty == "advanced" and self._award(user_id, "quiz_perfect_advanced"):
                unlocked.append("quiz_perfect_advanced")

        # Check streaks
        unlocked.extend(self._check_streak(user_id))
        return unlocked

    def _check_streak(self, user_id: int) -> list[str]:
        unlocked = []
        attempts = (
            QuizAttempt.query.filter_by(user_id=user_id, quiz_type="daily")
            .order_by(QuizAttempt.completed_at.desc())
            .all()
        )
        if not attempts:
            return unlocked

        dates = sorted(set(a.completed_at.date() for a in attempts if a.completed_at), reverse=True)
        streak = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == timedelta(days=1):
                streak += 1
            else:
                break

        if streak >= 3 and self._award(user_id, "daily_streak_3"):
            unlocked.append("daily_streak_3")
        if streak >= 7 and self._award(user_id, "daily_streak_7"):
            unlocked.append("daily_streak_7")
        if streak >= 30 and self._award(user_id, "daily_streak_30"):
            unlocked.append("daily_streak_30")

        return unlocked

    def _check_species_achievements(self, user_id: int, context: dict) -> list[str]:
        unlocked = []
        viewed = context.get("total_viewed", 0)
        total_species = context.get("total_species", 0)

        if viewed >= 50 and self._award(user_id, "species_explorer_50"):
            unlocked.append("species_explorer_50")
        if total_species > 0 and viewed >= total_species:
            if self._award(user_id, "species_explorer_all"):
                unlocked.append("species_explorer_all")
        return unlocked

    def _check_study_achievements(self, user_id: int) -> list[str]:
        unlocked = []
        total_sec = (
            db.session.query(db.func.sum(StudySession.duration_sec))
            .filter_by(user_id=user_id)
            .scalar()
        ) or 0

        if total_sec >= 3600 and self._award(user_id, "study_time_1h"):
            unlocked.append("study_time_1h")
        if total_sec >= 36000 and self._award(user_id, "study_time_10h"):
            unlocked.append("study_time_10h")
        return unlocked

    def get_user_achievements(self, user_id: int) -> list[dict]:
        earned = {
            a.achievement_key: a.unlocked_at
            for a in Achievement.query.filter_by(user_id=user_id).all()
        }
        result = []
        for item in self._catalogue:
            result.append(
                {
                    **item,
                    "unlocked": item["id"] in earned,
                    "unlocked_at": earned.get(item["id"]),
                }
            )
        return result

    def get_progress(self, user_id: int) -> dict:
        lessons_done = LessonProgress.query.filter_by(
            user_id=user_id, completed=True
        ).count()
        quizzes = QuizAttempt.query.filter_by(user_id=user_id).all()
        total_study = (
            db.session.query(db.func.sum(StudySession.duration_sec))
            .filter_by(user_id=user_id)
            .scalar()
        ) or 0

        avg_score = 0
        best_score = 0
        if quizzes:
            scores = [q.score / q.total * 100 for q in quizzes if q.total > 0]
            if scores:
                avg_score = round(sum(scores) / len(scores), 1)
                best_score = round(max(scores), 1)

        return {
            "lessons_completed": lessons_done,
            "quizzes_taken": len(quizzes),
            "avg_score": avg_score,
            "best_score": best_score,
            "study_time_hours": round(total_study / 3600, 1),
        }
