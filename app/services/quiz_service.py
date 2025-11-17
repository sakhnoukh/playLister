"""Quiz service for managing user feedback."""

import random
import sqlite3
from typing import List, Dict, Any, Set

from ..database import dict_factory


class QuizService:
    """Service for quiz operations."""
    
    @staticmethod
    def get_quiz_songs(
        db: sqlite3.Connection,
        user_id: int,
        n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get N random songs for quiz, preferring unrated songs.
        
        Args:
            db: Database connection
            user_id: User ID
            n: Number of songs to return
            
        Returns:
            List of song dicts
        """
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        
        # Get all songs
        cursor.execute("SELECT * FROM songs")
        all_songs = cursor.fetchall()
        
        if len(all_songs) < n:
            raise ValueError("Not enough songs in database")
        
        # Get already rated songs
        cursor.execute("SELECT song_id FROM user_song_feedback WHERE user_id = ?", (user_id,))
        rated_song_ids: Set[int] = {row["song_id"] for row in cursor.fetchall()}
        
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
    
    @staticmethod
    def save_feedback(
        db: sqlite3.Connection,
        user_id: int,
        song_id: int,
        liked: bool
    ) -> None:
        """
        Save or update user feedback for a song.
        
        Args:
            db: Database connection
            user_id: User ID
            song_id: Song ID
            liked: Whether user liked the song
        """
        cursor = db.cursor()
        
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
    
    @staticmethod
    def get_user_feedback(
        db: sqlite3.Connection,
        user_id: int
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Get user's liked and disliked songs.
        
        Args:
            db: Database connection
            user_id: User ID
            
        Returns:
            Tuple of (liked_songs, disliked_songs)
        """
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        
        # Get user's feedback
        cursor.execute("SELECT * FROM user_song_feedback WHERE user_id = ?", (user_id,))
        feedbacks = cursor.fetchall()
        
        liked_songs = []
        disliked_songs = []
        
        for feedback in feedbacks:
            cursor.execute("SELECT * FROM songs WHERE id = ?", (feedback["song_id"],))
            song = cursor.fetchone()
            
            if feedback["liked"]:
                liked_songs.append(song)
            else:
                disliked_songs.append(song)
        
        return liked_songs, disliked_songs
