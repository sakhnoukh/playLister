"""Database utilities and initialization."""

import csv
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

from flask import g, current_app


def get_db() -> sqlite3.Connection:
    """Get database connection for current request context."""
    db = getattr(g, '_database', None)
    if db is None:
        db_path = current_app.config.get("DATABASE_URL", "sqlite:///playlist.db")
        # Remove sqlite:/// prefix if present
        if db_path.startswith("sqlite:///"):
            db_path = db_path[10:]
        
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db


def close_db(exception: Optional[Exception] = None) -> None:
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    """Convert SQL row to dict."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def health_check_db() -> tuple[bool, float]:
    """
    Perform a simple database health check.
    
    Returns:
        Tuple of (is_healthy: bool, latency_ms: float)
    """
    import time
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        start = time.time()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        latency_ms = (time.time() - start) * 1000
        
        return True, latency_ms
    except Exception:
        return False, 0.0


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables and seed data if needed."""
    if db_path is None:
        db_path = "playlist.db"
    elif db_path.startswith("sqlite:///"):
        db_path = db_path[10:]
    
    conn = sqlite3.connect(db_path)
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


def seed_songs(conn: sqlite3.Connection) -> None:
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
