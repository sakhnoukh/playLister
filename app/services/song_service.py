"""Song service for song operations."""

import sqlite3
from typing import List, Dict, Any, Optional

from ..database import dict_factory


class SongService:
    """Service for song operations."""
    
    @staticmethod
    def get_all_songs(db: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Get all songs."""
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute("SELECT * FROM songs")
        return cursor.fetchall()
    
    @staticmethod
    def search_songs(
        db: sqlite3.Connection,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        titles_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search and filter songs.
        
        Args:
            db: Database connection
            search: Search term for title/artist
            genre: Genre filter
            titles_only: Return only id, title, artist
            
        Returns:
            List of song dicts
        """
        if titles_only:
            query = "SELECT id, title, artist FROM songs ORDER BY title"
            cursor = db.cursor()
            cursor.row_factory = dict_factory
            cursor.execute(query)
            return cursor.fetchall()
        
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
        
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute(query, params)
        return cursor.fetchall()
    
    @staticmethod
    def get_song_by_id(db: sqlite3.Connection, song_id: int) -> Optional[Dict[str, Any]]:
        """Get song by ID."""
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        return cursor.fetchone()
    
    @staticmethod
    def search_song_by_name(db: sqlite3.Connection, name: str) -> Optional[Dict[str, Any]]:
        """Search for song by partial name match."""
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute("SELECT * FROM songs WHERE title LIKE ? LIMIT 1", (f'%{name}%',))
        return cursor.fetchone()
