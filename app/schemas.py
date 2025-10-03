"""Pydantic schemas for API request/response models."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# User schemas
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


# Song schemas
class SongResponse(BaseModel):
    id: int
    title: str
    artist: str
    subgenre: str
    year: int
    tags: str
    bpm: Optional[int] = None


# Quiz schemas
class QuizStartRequest(BaseModel):
    user_id: int
    n: int = Field(default=10, ge=5, le=20)


class QuizAnswerRequest(BaseModel):
    user_id: int
    song_id: int
    liked: bool


# Playlist schemas
class PlaylistGenerateRequest(BaseModel):
    user_id: int
    count: int = Field(ge=5, le=100)
    genre: Optional[str] = None
    seed_song_id: Optional[int] = None


class PlaylistCreateRequest(BaseModel):
    user_id: int
    name: str
    song_ids: list[int]


class PlaylistSongResponse(BaseModel):
    song: SongResponse
    position: int


class PlaylistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    song_count: Optional[int] = None


class PlaylistDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    songs: list[PlaylistSongResponse]
