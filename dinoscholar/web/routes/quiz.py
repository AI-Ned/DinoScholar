import json
from flask import Blueprint, render_template, request, redirect, url_for, g, current_app, session
from datetime import datetime, timezone

from database import db
from models.quiz import QuizAttempt

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/")
def hub():
    svc = current_app.config["LEARNING_SERVICE"]
    modules = svc.get_modules()
    return render_template("quiz/hub.html", modules=modules)


@quiz_bp.route("/module/<module_id>")
def module_quiz(module_id):
    engine = current_app.config["QUIZ_ENGINE"]
    difficulty = request.args.get("difficulty", "all")
    questions = engine.generate_module_quiz(module_id, difficulty=difficulty)
    session["quiz_questions"] = _serialize_questions(questions)
    session["quiz_type"] = "module"
    session["quiz_module"] = module_id
    session["quiz_difficulty"] = difficulty
    session["quiz_start"] = datetime.now(timezone.utc).isoformat()
    return render_template(
        "quiz/take.html",
        questions=questions,
        quiz_type="module",
        module_id=module_id,
        timed=False,
    )


@quiz_bp.route("/daily")
def daily_challenge():
    engine = current_app.config["QUIZ_ENGINE"]
    questions = engine.generate_daily_challenge()
    session["quiz_questions"] = _serialize_questions(questions)
    session["quiz_type"] = "daily"
    session["quiz_module"] = None
    session["quiz_difficulty"] = "mixed"
    session["quiz_start"] = datetime.now(timezone.utc).isoformat()
    return render_template(
        "quiz/take.html",
        questions=questions,
        quiz_type="daily",
        module_id=None,
        timed=False,
    )


@quiz_bp.route("/timed")
def timed_quiz():
    engine = current_app.config["QUIZ_ENGINE"]
    difficulty = request.args.get("difficulty", "all")
    count = request.args.get("count", 20, type=int)
    questions = engine.generate_timed_quiz(difficulty=difficulty, count=count)
    session["quiz_questions"] = _serialize_questions(questions)
    session["quiz_type"] = "timed"
    session["quiz_module"] = None
    session["quiz_difficulty"] = difficulty
    session["quiz_start"] = datetime.now(timezone.utc).isoformat()
    return render_template(
        "quiz/take.html",
        questions=questions,
        quiz_type="timed",
        module_id=None,
        timed=True,
        time_limit_sec=300,
    )


@quiz_bp.route("/submit", methods=["POST"])
def submit():
    engine = current_app.config["QUIZ_ENGINE"]
    raw_questions = session.get("quiz_questions", [])
    questions = _deserialize_questions(raw_questions)

    answers = []
    for i, q in enumerate(questions):
        ans = request.form.get(f"answer_{i}", "")
        answers.append(ans)

    result = engine.score(questions, answers)

    # Record attempt
    if g.user:
        start_str = session.get("quiz_start")
        started_at = datetime.fromisoformat(start_str) if start_str else None
        completed_at = datetime.now(timezone.utc)
        duration = None
        if started_at:
            duration = int((completed_at - started_at).total_seconds())
        result.duration_sec = duration

        attempt = QuizAttempt(
            user_id=g.user.id,
            quiz_type=session.get("quiz_type", "module"),
            module_id=session.get("quiz_module"),
            score=result.score,
            total=result.total,
            difficulty=session.get("quiz_difficulty", "all"),
            started_at=started_at,
            completed_at=completed_at,
        )
        db.session.add(attempt)
        db.session.commit()

        # Check achievements
        achievement_svc = current_app.config.get("ACHIEVEMENT_SERVICE")
        if achievement_svc:
            achievement_svc.check_and_award(
                g.user.id,
                "quiz_submitted",
                {
                    "score": result.score,
                    "total": result.total,
                    "difficulty": session.get("quiz_difficulty", "all"),
                },
            )

    # Cleanup session
    for key in ["quiz_questions", "quiz_type", "quiz_module", "quiz_difficulty", "quiz_start"]:
        session.pop(key, None)

    return render_template("quiz/results.html", result=result)


def _serialize_questions(questions):
    return [
        {
            "id": q.id,
            "type": q.type,
            "difficulty": q.difficulty,
            "question": q.question,
            "options": q.options,
            "correct": q.correct,
            "explanation": q.explanation,
            "module_id": q.module_id,
            "lesson_id": q.lesson_id,
        }
        for q in questions
    ]


def _deserialize_questions(raw_list):
    from services.quiz_engine import Question
    return [
        Question(
            id=r["id"],
            type=r["type"],
            difficulty=r["difficulty"],
            question=r["question"],
            options=r.get("options"),
            correct=r["correct"],
            explanation=r.get("explanation", ""),
            module_id=r.get("module_id", ""),
            lesson_id=r.get("lesson_id", ""),
        )
        for r in raw_list
    ]
