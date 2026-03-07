from web.routes.main import main_bp
from web.routes.encyclopedia import encyclopedia_bp
from web.routes.timeline import timeline_bp
from web.routes.learning import learning_bp
from web.routes.quiz import quiz_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(encyclopedia_bp, url_prefix="/encyclopedia")
    app.register_blueprint(timeline_bp, url_prefix="/timeline")
    app.register_blueprint(learning_bp, url_prefix="/learn")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
