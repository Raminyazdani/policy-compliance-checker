from .health import health_bp
from .policies import policies_bp
from .users import users_bp
from .evaluate import eval_bp

def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(policies_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(eval_bp)
