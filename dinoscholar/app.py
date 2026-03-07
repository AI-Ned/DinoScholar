import os
import sys

from flask import Flask
from database import db, init_db
from web.routes import register_routes
from services.encyclopedia import EncyclopediaService
from services.timeline import TimelineService
from services.learning import LearningService
from services.quiz_engine import QuizEngine
from services.comparison import ComparisonService
from services.achievements import AchievementService


def create_app(config_class=None):
    app = Flask(
        __name__,
        template_folder="web/templates",
        static_folder="web/static",
    )

    if config_class:
        app.config.from_object(config_class)
    else:
        from config import DefaultConfig
        app.config.from_object(DefaultConfig)

    db.init_app(app)

    data_dir = app.config.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))

    # Initialize services
    enc_svc = EncyclopediaService(data_dir)
    timeline_svc = TimelineService(data_dir, encyclopedia_service=enc_svc)
    learning_svc = LearningService(data_dir)
    quiz_engine = QuizEngine(learning_svc)
    comparison_svc = ComparisonService(enc_svc)
    achievement_svc = AchievementService(data_dir)

    # Store services on app config for route access
    app.config["ENCYCLOPEDIA_SERVICE"] = enc_svc
    app.config["TIMELINE_SERVICE"] = timeline_svc
    app.config["LEARNING_SERVICE"] = learning_svc
    app.config["QUIZ_ENGINE"] = quiz_engine
    app.config["COMPARISON_SERVICE"] = comparison_svc
    app.config["ACHIEVEMENT_SERVICE"] = achievement_svc

    register_routes(app)

    with app.app_context():
        import models  # noqa: F401 — ensures all models are registered
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
