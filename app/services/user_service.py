"""User service for user management."""

import sqlite3
from typing import Optional, Dict, Any

from ..database import dict_factory


class UserService:
    """Service for user operations."""
    
    @staticmethod
    def get_or_create_user(db: sqlite3.Connection, name: str) -> Dict[str, Any]:
        """
        Get existing user or create new user by name.
        
        Args:
            db: Database connection
            name: User name
            
        Returns:
            User dict
        """
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
    
    @staticmethod
    def get_user_by_id(db: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            db: Database connection
            user_id: User ID
            
        Returns:
            User dict or None if not found
        """
        cursor = db.cursor()
        cursor.row_factory = dict_factory
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
