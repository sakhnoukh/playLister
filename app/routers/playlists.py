"""Playlist generation and management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from app.db import get_session
from app.models import User, Playlist, PlaylistSong, Song
from app.schemas import (
    PlaylistGenerateRequest,
    PlaylistCreateRequest,
    PlaylistResponse,
    PlaylistDetailResponse,
    PlaylistSongResponse,
    SongResponse
)
from app.services.recommender import PlaylistRecommender

router = APIRouter(prefix="/api/playlists", tags=["playlists"])


@router.post("/generate", response_model=list[SongResponse])
def generate_playlist(
    request: PlaylistGenerateRequest,
    session: Session = Depends(get_session)
):
    """Generate a playlist preview based on user taste (not saved yet)."""
    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify seed song if provided
    if request.seed_song_id:
        seed_song = session.get(Song, request.seed_song_id)
        if not seed_song:
            raise HTTPException(status_code=404, detail="Seed song not found")
    
    # Generate playlist
    recommender = PlaylistRecommender(session)
    songs = recommender.generate_playlist(
        user_id=request.user_id,
        count=request.count,
        genre=request.genre,
        seed_song_id=request.seed_song_id
    )
    
    return songs


@router.post("", response_model=dict)
def create_playlist(
    request: PlaylistCreateRequest,
    session: Session = Depends(get_session)
):
    """Save a playlist to user's profile."""
    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify all songs exist
    for song_id in request.song_ids:
        song = session.get(Song, song_id)
        if not song:
            raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Create playlist
    playlist = Playlist(
        user_id=request.user_id,
        name=request.name
    )
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    
    # Add songs to playlist
    for position, song_id in enumerate(request.song_ids, start=1):
        playlist_song = PlaylistSong(
            playlist_id=playlist.id,
            song_id=song_id,
            position=position
        )
        session.add(playlist_song)
    
    session.commit()
    
    return {"playlist_id": playlist.id}


@router.get("", response_model=list[PlaylistResponse])
def get_user_playlists(user_id: int, session: Session = Depends(get_session)):
    """Get all playlists for a user."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    playlists = session.exec(
        select(Playlist).where(Playlist.user_id == user_id)
    ).all()
    
    # Add song count to each playlist
    result = []
    for playlist in playlists:
        song_count = len(playlist.playlist_songs)
        result.append(
            PlaylistResponse(
                id=playlist.id,
                user_id=playlist.user_id,
                name=playlist.name,
                created_at=playlist.created_at,
                song_count=song_count
            )
        )
    
    return result


@router.get("/{playlist_id}", response_model=PlaylistDetailResponse)
def get_playlist(playlist_id: int, session: Session = Depends(get_session)):
    """Get detailed playlist with all songs."""
    playlist = session.get(Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Get playlist songs ordered by position
    playlist_songs = session.exec(
        select(PlaylistSong)
        .where(PlaylistSong.playlist_id == playlist_id)
        .order_by(PlaylistSong.position)
    ).all()
    
    songs_data = []
    for ps in playlist_songs:
        song = session.get(Song, ps.song_id)
        songs_data.append(
            PlaylistSongResponse(
                song=SongResponse(
                    id=song.id,
                    title=song.title,
                    artist=song.artist,
                    subgenre=song.subgenre,
                    year=song.year,
                    tags=song.tags,
                    bpm=song.bpm
                ),
                position=ps.position
            )
        )
    
    return PlaylistDetailResponse(
        id=playlist.id,
        user_id=playlist.user_id,
        name=playlist.name,
        created_at=playlist.created_at,
        songs=songs_data
    )


@router.delete("/{playlist_id}", status_code=204)
def delete_playlist(playlist_id: int, session: Session = Depends(get_session)):
    """Delete a playlist."""
    playlist = session.get(Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Delete associated playlist songs first
    playlist_songs = session.exec(
        select(PlaylistSong).where(PlaylistSong.playlist_id == playlist_id)
    ).all()
    
    for ps in playlist_songs:
        session.delete(ps)
    
    # Delete playlist
    session.delete(playlist)
    session.commit()
    
    return Response(status_code=204)
