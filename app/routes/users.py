"""User routes."""

from flask import Blueprint, request, jsonify

from ..database import get_db
from ..services.user_service import UserService

bp = Blueprint("users", __name__)


@bp.route("", methods=["POST"])
def create_user():
    """Create a new user or get existing user by name."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
        
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    try:
        db = get_db()
        user = UserService.get_or_create_user(db, name)
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
