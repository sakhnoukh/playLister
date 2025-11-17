"""Health check endpoints."""

from flask import Blueprint, jsonify, current_app

from ..database import health_check_db

bp = Blueprint("health", __name__)


@bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    
    Returns JSON with app status, version, and database health.
    """
    db_ok, latency_ms = health_check_db()
    
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "version": current_app.config.get("APP_VERSION", "0.0.0"),
        "db": "ok" if db_ok else "down",
        "latency_ms": round(latency_ms, 2)
    })
