"""Playlist routes."""

from flask import Blueprint, request, jsonify, current_app

from ..database import get_db
from ..config import get_config
from ..services.user_service import UserService
from ..services.song_service import SongService
from ..services.quiz_service import QuizService
from ..services.playlist_service import PlaylistService
from ..services.recommender import RecommenderService
from ..routes.metrics import playlist_generate_total

bp = Blueprint("playlists", __name__)


@bp.route("/generate", methods=["POST"])
def generate_playlist():
    """Generate a playlist based on user taste."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
        
    user_id = data.get("user_id")
    count = data.get("count", 20)
    genre = data.get("genre")
    seed_song_name = data.get("seed_song_name")
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        db = get_db()
        
        # Verify user exists
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            # Track failure
            if playlist_generate_total:
                playlist_generate_total.labels(success='false', genre=genre or 'none').inc()
            return jsonify({"error": "User not found"}), 404
        
        # Get all songs
        all_songs = SongService.get_all_songs(db)
        
        # Get user's feedback
        liked_songs, disliked_songs = QuizService.get_user_feedback(db, user_id)
        
        # Get seed song if specified
        seed_song = None
        if seed_song_name:
            seed_song = SongService.search_song_by_name(db, seed_song_name)
            if not seed_song:
                # Track failure
                if playlist_generate_total:
                    playlist_generate_total.labels(success='false', genre=genre or 'none').inc()
                return jsonify({"error": f"No song found matching '{seed_song_name}'"}), 404
        
        # Initialize recommender
        config = get_config()
        recommender = RecommenderService(config)
        
        # Generate recommendations
        if not liked_songs and not disliked_songs:
            # Cold start - no feedback yet
            result = recommender.generate_cold_start_playlist(all_songs, count, genre)
        else:
            # Generate based on taste profile
            result = recommender.generate_recommendations(
                all_songs, liked_songs, disliked_songs, count, genre, seed_song
            )
        
        # Track success
        if playlist_generate_total:
            playlist_generate_total.labels(success='true', genre=genre or 'none').inc()
        
        return jsonify(result), 200
    except Exception as e:
        # Track failure
        if playlist_generate_total:
            playlist_generate_total.labels(success='false', genre=genre or 'none').inc()
        return jsonify({"error": str(e)}), 500


@bp.route("", methods=["POST"])
def create_playlist():
    """Save a playlist to user's profile."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
        
    user_id = data.get("user_id")
    name = data.get("name")
    song_ids = data.get("song_ids", [])
    
    if not all([user_id, name, song_ids]):
        return jsonify({"error": "user_id, name, and song_ids are required"}), 400
    
    try:
        db = get_db()
        
        # Verify user exists
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify all songs exist
        for song_id in song_ids:
            song = SongService.get_song_by_id(db, song_id)
            if not song:
                return jsonify({"error": f"Song {song_id} not found"}), 404
        
        # Create playlist
        playlist_id = PlaylistService.create_playlist(db, user_id, name, song_ids)
        
        return jsonify({"playlist_id": playlist_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("", methods=["GET"])
def get_user_playlists():
    """Get all playlists for a user."""
    user_id = request.args.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        db = get_db()
        
        # Verify user exists
        user = UserService.get_user_by_id(db, int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get playlists
        playlists = PlaylistService.get_user_playlists(db, int(user_id))
        
        return jsonify(playlists), 200
    except ValueError:
        return jsonify({"error": "Invalid user_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:playlist_id>", methods=["GET"])
def get_playlist(playlist_id):
    """Get detailed playlist with all songs."""
    try:
        db = get_db()
        
        # Get playlist
        playlist = PlaylistService.get_playlist_by_id(db, playlist_id)
        if not playlist:
            return jsonify({"error": "Playlist not found"}), 404
        
        return jsonify(playlist), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id):
    """Delete a playlist."""
    try:
        db = get_db()
        
        # Delete playlist
        deleted = PlaylistService.delete_playlist(db, playlist_id)
        if not deleted:
            return jsonify({"error": "Playlist not found"}), 404
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
