"""Song routes."""

from flask import Blueprint, request, jsonify

from ..database import get_db
from ..services.song_service import SongService

bp = Blueprint("songs", __name__)


@bp.route("", methods=["GET"])
def get_songs():
    """Get songs with optional filtering."""
    search = request.args.get('search')
    genre = request.args.get('genre')
    titles_only = request.args.get('titles_only') == 'true'
    
    try:
        db = get_db()
        songs = SongService.search_songs(db, search=search, genre=genre, titles_only=titles_only)
        return jsonify(songs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
