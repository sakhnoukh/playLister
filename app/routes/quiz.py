"""Quiz routes."""

from flask import Blueprint, request, jsonify

from ..database import get_db
from ..services.user_service import UserService
from ..services.song_service import SongService
from ..services.quiz_service import QuizService

bp = Blueprint("quiz", __name__)


@bp.route("/start", methods=["POST"])
def start_quiz():
    """Start a quiz by getting N random songs."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
        
    user_id = data.get("user_id")
    n = data.get("n", 10)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        db = get_db()
        
        # Verify user exists
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get quiz songs
        songs = QuizService.get_quiz_songs(db, user_id, n)
        return jsonify(songs), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/answer", methods=["POST"])
def answer_quiz():
    """Record user's like/dislike for a song."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
        
    user_id = data.get("user_id")
    song_id = data.get("song_id")
    liked = data.get("liked")
    
    if not all([user_id, song_id, liked is not None]):
        return jsonify({"error": "user_id, song_id, and liked are required"}), 400
    
    try:
        db = get_db()
        
        # Verify user exists
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify song exists
        song = SongService.get_song_by_id(db, song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404
        
        # Save feedback
        QuizService.save_feedback(db, user_id, song_id, liked)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
