"""Playlist service for playlist management."""

import sqlite3
from typing import List, Dict, Any, Optional

from ..database import dict_factory


class PlaylistService:
    """Service for playlist operations."""
    
    @staticmethod
    def create_playlist(
        db: sqlite3.Connection,
        user_id: int,
        name: str,
        song_ids: List[int]
    ) -> int:
        """
        Create and save a playlist.
        
        Args:
            db: Database connection
            user_id: User ID
            name: Playlist name
            song_ids: List of song IDs
            
        Returns:
            New playlist ID
        """
        cursor = db.cursor()
        
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
        
        return playlist_id
    
    @staticmethod
    def get_user_playlists(
        db: sqlite3.Connection,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all playlists for a user.
        
        Args:
            db: Database connection
            user_id: User ID
            
        Returns:
            List of playlist dicts with song counts
        """
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        
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
    
    @staticmethod
    def get_playlist_by_id(
        db: sqlite3.Connection,
        playlist_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed playlist with all songs.
        
        Args:
            db: Database connection
            playlist_id: Playlist ID
            
        Returns:
            Playlist dict with songs or None if not found
        """
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        
        # Get playlist
        cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
        playlist = cursor.fetchone()
        if not playlist:
            return None
        
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
    
    @staticmethod
    def delete_playlist(db: sqlite3.Connection, playlist_id: int) -> bool:
        """
        Delete a playlist.
        
        Args:
            db: Database connection
            playlist_id: Playlist ID
            
        Returns:
            True if deleted, False if not found
        """
        cursor = db.cursor()
        
        # Verify playlist exists
        cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
        playlist = cursor.fetchone()
        if not playlist:
            return False
        
        # Delete playlist songs first
        cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
        
        # Delete playlist
        cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        
        db.commit()
        return True
