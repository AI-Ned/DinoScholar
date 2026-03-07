from flask import Blueprint, render_template, request, redirect, url_for, session, g
from datetime import datetime, timezone

from database import db
from models.user import User
from models.progress import LessonProgress

main_bp = Blueprint("main", __name__)


@main_bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    if user_id:
        g.user = User.query.get(user_id)
        if g.user:
            g.user.last_active = datetime.now(timezone.utc)
            db.session.commit()
    else:
        g.user = None


@main_bp.route("/")
def home():
    if not g.user:
        return render_template("welcome.html")
    return render_template("home.html", user=g.user)


@main_bp.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    if not username:
        return redirect(url_for("main.home"))
    existing = User.query.filter_by(username=username).first()
    if existing:
        session["user_id"] = existing.id
        return redirect(url_for("main.home"))
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return redirect(url_for("main.home"))


@main_bp.route("/dashboard")
def dashboard():
    if not g.user:
        return redirect(url_for("main.home"))
    from flask import current_app
    achievement_svc = current_app.config.get("ACHIEVEMENT_SERVICE")
    learning_svc = current_app.config.get("LEARNING_SERVICE")

    progress_data = {}
    module_progress = []
    if learning_svc:
        for module in learning_svc.get_modules():
            total = len(module.lessons)
            completed = LessonProgress.query.filter_by(
                user_id=g.user.id, module_id=module.id, completed=True
            ).count()
            module_progress.append({
                "module": module,
                "total": total,
                "completed": completed,
                "percent": round(completed / total * 100) if total > 0 else 0,
            })

    achievements = []
    if achievement_svc:
        progress_data = achievement_svc.get_progress(g.user.id)
        achievements = achievement_svc.get_user_achievements(g.user.id)

    return render_template(
        "dashboard.html",
        user=g.user,
        module_progress=module_progress,
        progress=progress_data,
        achievements=achievements,
    )


@main_bp.route("/glossary/")
def glossary():
    from flask import current_app
    learning_svc = current_app.config.get("LEARNING_SERVICE")
    terms = []
    if learning_svc:
        glossary_data = learning_svc.get_glossary()
        terms = sorted(glossary_data.values(), key=lambda t: t["term"].lower())
    query = request.args.get("q", "").strip()
    if query:
        q = query.lower()
        terms = [t for t in terms if q in t["term"].lower() or q in t["definition"].lower()]
    return render_template("glossary.html", terms=terms, query=query)


@main_bp.route("/glossary/<term_id>")
def glossary_term(term_id):
    from flask import current_app
    learning_svc = current_app.config.get("LEARNING_SERVICE")
    term = None
    if learning_svc:
        term = learning_svc.get_glossary_term(term_id)
    if not term:
        return "Term not found", 404
    return render_template("glossary_term.html", term=term)
