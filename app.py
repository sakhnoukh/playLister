"""Flask version of the PlayLister app."""

import os
import csv
import json
import random
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, render_template, g

# Create Flask app
app = Flask(__name__, 
            static_folder="app/static", 
            template_folder="app/templates")

# Database setup
DB_PATH = "playlist.db"

def get_db():
    """Get database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        artist TEXT,
        subgenre TEXT,
        year INTEGER,
        tags TEXT,
        bpm INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_song_feedback (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        song_id INTEGER,
        liked BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (song_id) REFERENCES songs(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY,
        playlist_id INTEGER,
        song_id INTEGER,
        position INTEGER,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id),
        FOREIGN KEY (song_id) REFERENCES songs(id)
    )
    ''')
    
    # Check if songs table is empty
    cursor.execute("SELECT COUNT(*) FROM songs")
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_songs(conn)
    
    conn.commit()
    conn.close()

def seed_songs(conn):
    """Seed songs from CSV file."""
    seed_file = Path("seed/house_tracks.csv")
    cursor = conn.cursor()
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO songs (title, artist, subgenre, year, tags, bpm) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    row["title"],
                    row["artist"],
                    row["subgenre"],
                    int(row["year"]),
                    row["tags"],
                    int(row["bpm"]) if row["bpm"] else None
                )
            )
    
    conn.commit()

# Helper function to convert sqlite3.Row to dict
def dict_factory(cursor, row):
    """Convert SQL row to dict."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def json_response(f):
    """Convert function result to JSON response."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, tuple):
                response, status_code = result
                return jsonify(response), status_code
            return jsonify(result)
        except Exception as e:
            app.logger.error(f"Error in API endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function

# API Routes
@app.route("/api/health")
@json_response
def health():
    """Health check endpoint."""
    return {"status": "ok", "app": "PlayLister", "version": "1.0.0"}

@app.route("/api/users", methods=["POST"])
@json_response
def create_user():
    """Create a new user or get existing user by name."""
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400
        
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON"}, 400
        
    name = data.get("name")
    if not name:
        return {"error": "Name is required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    
    if user:
        return user
    
    # Create new user
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    db.commit()
    
    # Get the new user
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    
    return user

@app.route("/api/songs")
@json_response
def get_songs():
    """Get songs with optional filtering."""
    search = request.args.get('search')
    genre = request.args.get('genre')
    titles_only = request.args.get('titles_only') == 'true'
    
    if titles_only:
        query = "SELECT id, title, artist FROM songs ORDER BY title"
        db = get_db()
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute(query)
        songs = cursor.fetchall()
        return songs
    
    query = "SELECT * FROM songs"
    params = []
    
    # Build where clause
    where_clauses = []
    
    if search:
        where_clauses.append("(title LIKE ? OR artist LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])
    
    if genre:
        where_clauses.append("subgenre = ?")
        params.append(genre)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    cursor.execute(query, params)
    songs = cursor.fetchall()
    
    return songs


@app.route("/api/quiz/start", methods=["POST"])
@json_response
def start_quiz():
    """Start a quiz by getting N random songs."""
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400
        
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON"}, 400
        
    user_id = data.get("user_id")
    n = data.get("n", 10)
    
    if not user_id:
        return {"error": "user_id is required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    
    # Verify user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    
    # Get all songs
    cursor.execute("SELECT * FROM songs")
    all_songs = cursor.fetchall()
    
    if len(all_songs) < n:
        return {"error": "Not enough songs in database"}, 400
    
    # Get already rated songs
    cursor.execute("SELECT song_id FROM user_song_feedback WHERE user_id = ?", (user_id,))
    rated_song_ids = {row["song_id"] for row in cursor.fetchall()}
    
    # Filter out already rated songs
    unrated_songs = [s for s in all_songs if s["id"] not in rated_song_ids]
    
    # If not enough unrated songs, include some rated ones
    if len(unrated_songs) < n:
        rated_songs = [s for s in all_songs if s["id"] in rated_song_ids]
        songs_to_return = unrated_songs + random.sample(
            rated_songs,
            min(n - len(unrated_songs), len(rated_songs))
        )
    else:
        songs_to_return = random.sample(unrated_songs, n)
    
    return songs_to_return

@app.route("/api/quiz/answer", methods=["POST"])
@json_response
def answer_quiz():
    """Record user's like/dislike for a song."""
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400
        
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON"}, 400
        
    user_id = data.get("user_id")
    song_id = data.get("song_id")
    liked = data.get("liked")
    
    if not all([user_id, song_id, liked is not None]):
        return {"error": "user_id, song_id, and liked are required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    
    # Verify song exists
    cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
    song = cursor.fetchone()
    if not song:
        return {"error": "Song not found"}, 404
    
    # Check if feedback already exists
    cursor.execute(
        "SELECT * FROM user_song_feedback WHERE user_id = ? AND song_id = ?",
        (user_id, song_id)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing feedback
        cursor.execute(
            "UPDATE user_song_feedback SET liked = ? WHERE id = ?",
            (liked, existing["id"])
        )
    else:
        # Create new feedback
        cursor.execute(
            "INSERT INTO user_song_feedback (user_id, song_id, liked) VALUES (?, ?, ?)",
            (user_id, song_id, liked)
        )
    
    db.commit()
    return {"status": "success"}

def _score_song(song, liked_songs, disliked_songs, seed_song):
    """Calculate recommendation score for a song."""
    score = 0.0
    
    # Artist affinity
    for liked in liked_songs:
        if song["artist"] == liked["artist"]:
            score += 2.0
    
    for disliked in disliked_songs:
        if song["artist"] == disliked["artist"]:
            score -= 2.0
    
    # Subgenre affinity
    for liked in liked_songs:
        if song["subgenre"] == liked["subgenre"]:
            score += 1.0
    
    for disliked in disliked_songs:
        if song["subgenre"] == disliked["subgenre"]:
            score -= 1.0
    
    # Tag overlap with liked songs
    song_tags = set(song["tags"].split(';')) if song["tags"] else set()
    for liked in liked_songs:
        liked_tags = set(liked["tags"].split(';')) if liked["tags"] else set()
        overlap = song_tags & liked_tags
        score += len(overlap) * 0.5
    
    # BPM proximity
    if song["bpm"] and liked_songs:
        liked_bpms = [s["bpm"] for s in liked_songs if s["bpm"]]
        if liked_bpms:
            median_bpm = sum(liked_bpms) / len(liked_bpms)
            if abs(song["bpm"] - median_bpm) <= 8:
                score += 0.3
    
    # Era proximity
    if liked_songs:
        liked_years = [s["year"] for s in liked_songs]
        median_year = sum(liked_years) / len(liked_years)
        if abs(song["year"] - median_year) <= 5:
            score += 0.2
    
    # Seed song similarity
    if seed_song:
        if song["artist"] == seed_song["artist"]:
            score += 1.0
        if song["subgenre"] == seed_song["subgenre"]:
            score += 1.0
        
        seed_tags = set(seed_song["tags"].split(';')) if seed_song["tags"] else set()
        tag_overlap = song_tags & seed_tags
        score += len(tag_overlap) * 1.0
        
        if song["bpm"] and seed_song["bpm"] and abs(song["bpm"] - seed_song["bpm"]) <= 8:
            score += 0.3
    
    # Add small random jitter to avoid ties
    score += random.uniform(0, 0.1)
    
    return score

@app.route("/api/playlists/generate", methods=["POST"])
@json_response
def generate_playlist():
    """Generate a playlist based on user taste."""
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400
        
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON"}, 400
        
    user_id = data.get("user_id")
    count = data.get("count", 20)
    genre = data.get("genre")
    seed_song_name = data.get("seed_song_name")
    
    if not user_id:
        return {"error": "user_id is required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    
    # Verify user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    
    # Get user's feedback
    cursor.execute("SELECT * FROM user_song_feedback WHERE user_id = ?", (user_id,))
    feedbacks = cursor.fetchall()
    
    if not feedbacks:
        # No feedback yet - return a mix of genre-specific and random songs
        preferred_songs = []
        
        # First try to get songs from the specified genre
        if genre:
            cursor.execute("SELECT * FROM songs WHERE subgenre = ?", (genre,))
            preferred_songs = cursor.fetchall()
        
        # Get all songs
        cursor.execute("SELECT * FROM songs")
        all_songs = cursor.fetchall()
        
        # If we have enough songs in the preferred genre
        if genre and len(preferred_songs) >= count:
            return random.sample(preferred_songs, count)
        
        # Otherwise create a mixed playlist
        result = []
        
        # First add all songs from the preferred genre
        if genre:
            result.extend(preferred_songs)
        
        # Then add random songs that aren't already in the result
        remaining_songs = [song for song in all_songs if not any(song["id"] == s["id"] for s in result)]
        needed = count - len(result)
        
        if needed > 0 and remaining_songs:
            result.extend(random.sample(remaining_songs, min(needed, len(remaining_songs))))
        
        return result
    
    # Build taste profile
    liked_songs = []
    disliked_songs = []
    disliked_song_ids = set()
    
    for feedback in feedbacks:
        cursor.execute("SELECT * FROM songs WHERE id = ?", (feedback["song_id"],))
        song = cursor.fetchone()
        
        if feedback["liked"]:
            liked_songs.append(song)
        else:
            disliked_songs.append(song)
            disliked_song_ids.add(song["id"])
    
    # Get seed song if specified
    seed_song = None
    if seed_song_name:
        # Use LIKE for a more flexible search (case-insensitive partial match)
        cursor.execute("SELECT * FROM songs WHERE title LIKE ? LIMIT 1", (f'%{seed_song_name}%',))
        seed_song = cursor.fetchone()
        if not seed_song:
            return {"error": f"No song found matching '{seed_song_name}'"}, 404
    
    # First, get songs from the specified genre if any
    preferred_songs = []
    if genre:
        query = "SELECT * FROM songs WHERE subgenre = ?"
        cursor.execute(query, [genre])
        preferred_songs = cursor.fetchall()
    
    # Get all songs for backup/filling
    cursor.execute("SELECT * FROM songs")
    all_songs = cursor.fetchall()
    
    # Score each song
    scored_songs = []
    
    # First, process songs from the preferred genre if specified
    if genre and preferred_songs:
        for song in preferred_songs:
            if song["id"] in disliked_song_ids:
                continue
            
            # Give a genre bonus to preferred genre songs
            score = _score_song(song, liked_songs, disliked_songs, seed_song)
            score += 5.0  # Significant bonus for matching the requested genre
            scored_songs.append((song, score))
    
    # Then process all songs to fill the playlist if needed
    for song in all_songs:
        # Skip songs that are already scored or disliked
        if song["id"] in disliked_song_ids or any(s["id"] == song["id"] for s, _ in scored_songs):
            continue
        
        score = _score_song(song, liked_songs, disliked_songs, seed_song)
        scored_songs.append((song, score))
    
    # Sort by score and return top N
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    result = [song for song, _ in scored_songs[:count]]
    
    return result

@app.route("/api/playlists", methods=["POST"])
@json_response
def create_playlist():
    """Save a playlist to user's profile."""
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400
        
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON"}, 400
        
    user_id = data.get("user_id")
    name = data.get("name")
    song_ids = data.get("song_ids", [])
    
    if not all([user_id, name, song_ids]):
        return {"error": "user_id, name, and song_ids are required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    
    # Verify all songs exist
    for song_id in song_ids:
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        song = cursor.fetchone()
        if not song:
            return {"error": f"Song {song_id} not found"}, 404
    
    # Create playlist
    cursor.execute(
        "INSERT INTO playlists (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    playlist_id = cursor.lastrowid
    
    # Add songs to playlist
    for position, song_id in enumerate(song_ids, start=1):
        cursor.execute(
            "INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)",
            (playlist_id, song_id, position)
        )
    
    db.commit()
    
    return {"playlist_id": playlist_id}

@app.route("/api/playlists")
@json_response
def get_user_playlists():
    """Get all playlists for a user."""
    user_id = request.args.get("user_id")
    
    if not user_id:
        return {"error": "user_id is required"}, 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    
    # Verify user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    
    # Get playlists
    cursor.execute(
        "SELECT * FROM playlists WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    playlists = cursor.fetchall()
    
    # Add song count to each playlist
    for playlist in playlists:
        cursor.execute(
            "SELECT COUNT(*) as count FROM playlist_songs WHERE playlist_id = ?",
            (playlist["id"],)
        )
        song_count = cursor.fetchone()["count"]
        playlist["song_count"] = song_count
    
    return playlists

@app.route("/api/playlists/<int:playlist_id>")
@json_response
def get_playlist(playlist_id):
    """Get detailed playlist with all songs."""
    db = get_db()
    cursor = db.cursor()
    cursor.row_factory = dict_factory
    
    # Get playlist
    cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
    playlist = cursor.fetchone()
    if not playlist:
        return {"error": "Playlist not found"}, 404
    
    # Get playlist songs
    cursor.execute(
        """
        SELECT s.*, ps.position 
        FROM songs s 
        JOIN playlist_songs ps ON s.id = ps.song_id 
        WHERE ps.playlist_id = ? 
        ORDER BY ps.position
        """,
        (playlist_id,)
    )
    songs_data = cursor.fetchall()
    
    # Format response - structure songs as the frontend expects
    formatted_songs = []
    for song_data in songs_data:
        position = song_data.pop('position')
        formatted_songs.append({
            'position': position,
            'song': song_data
        })
    
    playlist["songs"] = formatted_songs
    
    return playlist

@app.route("/api/playlists/<int:playlist_id>", methods=["DELETE"])
@json_response
def delete_playlist(playlist_id):
    """Delete a playlist."""
    db = get_db()
    cursor = db.cursor()
    
    # Verify playlist exists
    cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
    playlist = cursor.fetchone()
    if not playlist:
        return {"error": "Playlist not found"}, 404
    
    # Delete playlist songs first
    cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
    
    # Delete playlist
    cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    
    db.commit()
    return {"status": "success"}

# Frontend routes
@app.route("/")
def home():
    """Home page - user login."""
    return render_template("home.html")

@app.route("/quiz")
def quiz_page():
    """Quiz page."""
    return render_template("quiz.html")

@app.route("/generate")
def generate_page():
    """Playlist generation page."""
    return render_template("generate.html")

@app.route("/profile")
def profile_page():
    """User profile with saved playlists."""
    return render_template("profile.html")

# Debug route removed

if __name__ == "__main__":
    init_db()
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    try:
        port = int(os.getenv('FLASK_PORT', '5050'))
    except ValueError as e:
        raise ValueError(f"FLASK_PORT must be an integer, got: {os.getenv('FLASK_PORT')}") from e
    app.run(debug=debug_mode, host=host, port=port)
