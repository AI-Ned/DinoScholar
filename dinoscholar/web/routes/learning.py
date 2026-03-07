from flask import Blueprint, render_template, request, redirect, url_for, g, current_app
from datetime import datetime, timezone

from database import db
from models.progress import LessonProgress

learning_bp = Blueprint("learning", __name__)


@learning_bp.route("/")
def modules():
    svc = current_app.config["LEARNING_SERVICE"]
    module_list = svc.get_modules()
    module_progress = []
    for module in module_list:
        total = len(module.lessons)
        completed = 0
        if g.user:
            completed = LessonProgress.query.filter_by(
                user_id=g.user.id, module_id=module.id, completed=True
            ).count()
        module_progress.append({
            "module": module,
            "total": total,
            "completed": completed,
            "percent": round(completed / total * 100) if total > 0 else 0,
        })
    return render_template("learning/modules.html", module_progress=module_progress)


@learning_bp.route("/<module_id>")
def module_detail(module_id):
    svc = current_app.config["LEARNING_SERVICE"]
    module = svc.get_module(module_id)
    if not module:
        return "Module not found", 404
    completed_ids = set()
    if g.user:
        progress = LessonProgress.query.filter_by(
            user_id=g.user.id, module_id=module_id, completed=True
        ).all()
        completed_ids = {p.lesson_id for p in progress}
    return render_template(
        "learning/module_detail.html",
        module=module,
        completed_ids=completed_ids,
    )


@learning_bp.route("/<module_id>/<lesson_id>")
def lesson(module_id, lesson_id):
    svc = current_app.config["LEARNING_SERVICE"]
    module = svc.get_module(module_id)
    if not module:
        return "Module not found", 404
    lesson_obj = svc.get_lesson(module_id, lesson_id)
    if not lesson_obj:
        return "Lesson not found", 404
    questions = svc.get_module_questions(module_id)
    is_completed = False
    if g.user:
        progress = LessonProgress.query.filter_by(
            user_id=g.user.id, module_id=module_id, lesson_id=lesson_id
        ).first()
        is_completed = progress and progress.completed

    # Find next lesson
    next_lesson = None
    for i, l in enumerate(module.lessons):
        if l.id == lesson_id and i + 1 < len(module.lessons):
            next_lesson = module.lessons[i + 1]
            break

    return render_template(
        "learning/lesson.html",
        module=module,
        lesson=lesson_obj,
        questions=questions,
        is_completed=is_completed,
        next_lesson=next_lesson,
    )


@learning_bp.route("/<module_id>/<lesson_id>/complete", methods=["POST"])
def mark_complete(module_id, lesson_id):
    if not g.user:
        return redirect(url_for("main.home"))
    progress = LessonProgress.query.filter_by(
        user_id=g.user.id, module_id=module_id, lesson_id=lesson_id
    ).first()
    if not progress:
        progress = LessonProgress(
            user_id=g.user.id,
            module_id=module_id,
            lesson_id=lesson_id,
        )
        db.session.add(progress)
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    # Check achievements
    achievement_svc = current_app.config.get("ACHIEVEMENT_SERVICE")
    learning_svc = current_app.config["LEARNING_SERVICE"]
    if achievement_svc:
        module = learning_svc.get_module(module_id)
        total_lessons = len(module.lessons) if module else 0
        achievement_svc.check_and_award(
            g.user.id,
            "lesson_completed",
            {"module_id": module_id, "total_lessons": total_lessons},
        )

    return redirect(url_for("learning.lesson", module_id=module_id, lesson_id=lesson_id))
