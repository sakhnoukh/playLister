"""Frontend routes for HTML templates."""

from flask import Blueprint, render_template

bp = Blueprint("frontend", __name__)


@bp.route("/")
def home():
    """Home page - user login."""
    return render_template("home.html")


@bp.route("/quiz")
def quiz_page():
    """Quiz page."""
    return render_template("quiz.html")


@bp.route("/generate")
def generate_page():
    """Playlist generation page."""
    return render_template("generate.html")


@bp.route("/profile")
def profile_page():
    """User profile with saved playlists."""
    return render_template("profile.html")
