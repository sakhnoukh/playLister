"""Flask application factory."""

from flask import Flask
from .config import get_config
from .database import close_db, init_db
from .routes import health, users, songs, quiz, playlists, frontend
from .routes.metrics import init_metrics


def create_app(config_name=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration name (development, production, test)
        
    Returns:
        Configured Flask app instance
    """
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Ensure the SQLite database exists and is seeded when the container starts
    with app.app_context():
        init_db(app.config.get("DATABASE_URL"))
    
    # Register blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(users.bp, url_prefix="/api/users")
    app.register_blueprint(songs.bp, url_prefix="/api/songs")
    app.register_blueprint(quiz.bp, url_prefix="/api/quiz")
    app.register_blueprint(playlists.bp, url_prefix="/api/playlists")
    app.register_blueprint(frontend.bp)
    
    # Initialize metrics (Prometheus)
    init_metrics(app)
    
    return app
