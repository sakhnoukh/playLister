"""SQLModel database models for the playlist generator."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    """User model - identified by name only (no auth in v1)."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    feedbacks: list["UserSongFeedback"] = Relationship(back_populates="user")
    playlists: list["Playlist"] = Relationship(back_populates="user")


class Song(SQLModel, table=True):
    """Song model with house music metadata."""
    __tablename__ = "songs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    artist: str = Field(index=True)
    subgenre: str = Field(index=True)
    year: int
    tags: str  # CSV format: "vocal;piano;classic"
    bpm: Optional[int] = None
    
    # Relationships
    feedbacks: list["UserSongFeedback"] = Relationship(back_populates="song")
    playlist_songs: list["PlaylistSong"] = Relationship(back_populates="song")


class UserSongFeedback(SQLModel, table=True):
    """User feedback on songs (like/dislike from quiz)."""
    __tablename__ = "user_song_feedback"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    song_id: int = Field(foreign_key="songs.id", index=True)
    liked: bool  # True = like, False = dislike
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="feedbacks")
    song: Song = Relationship(back_populates="feedbacks")


class Playlist(SQLModel, table=True):
    """User's saved playlists."""
    __tablename__ = "playlists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="playlists")
    playlist_songs: list["PlaylistSong"] = Relationship(back_populates="playlist")


class PlaylistSong(SQLModel, table=True):
    """Join table for playlist songs with ordering."""
    __tablename__ = "playlist_songs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    playlist_id: int = Field(foreign_key="playlists.id", index=True)
    song_id: int = Field(foreign_key="songs.id", index=True)
    position: int  # Order in the playlist
    
    # Relationships
    playlist: Playlist = Relationship(back_populates="playlist_songs")
    song: Song = Relationship(back_populates="playlist_songs")
