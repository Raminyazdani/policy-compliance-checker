from .health import health_bp
from .policies import policies_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(policies_bp)

