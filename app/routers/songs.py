"""Song browsing and search endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.db import get_session
from app.models import Song
from app.schemas import SongResponse

router = APIRouter(prefix="/api/songs", tags=["songs"])


@router.get("", response_model=list[SongResponse])
def get_songs(
    q: str = Query(default="", description="Search query for title or artist"),
    subgenre: str = Query(default="", description="Filter by subgenre"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    """Get songs with optional search and filtering."""
    statement = select(Song)
    
    # Apply filters
    if q:
        statement = statement.where(
            (Song.title.contains(q)) | (Song.artist.contains(q))
        )
    
    if subgenre:
        statement = statement.where(Song.subgenre == subgenre)
    
    # Apply pagination
    statement = statement.offset(offset).limit(limit)
    
    songs = session.exec(statement).all()
    return songs


@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: int, session: Session = Depends(get_session)):
    """Get a specific song by ID."""
    song = session.get(Song, song_id)
    if not song:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Song not found")
    return song
