"""Quiz endpoints for gathering user taste preferences."""

import random
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from app.db import get_session
from app.models import Song, User, UserSongFeedback
from app.schemas import QuizStartRequest, QuizAnswerRequest, SongResponse

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/start", response_model=list[SongResponse])
def start_quiz(request: QuizStartRequest, session: Session = Depends(get_session)):
    """Start a quiz by getting N random songs."""
    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all songs
    all_songs = session.exec(select(Song)).all()
    
    if len(all_songs) < request.n:
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough songs in database. Need {request.n}, have {len(all_songs)}"
        )
    
    # Get already rated songs to exclude them
    rated_statement = select(UserSongFeedback.song_id).where(
        UserSongFeedback.user_id == request.user_id
    )
    rated_song_ids = set(session.exec(rated_statement).all())
    
    # Filter out already rated songs
    unrated_songs = [s for s in all_songs if s.id not in rated_song_ids]
    
    # If not enough unrated songs, include some rated ones
    if len(unrated_songs) < request.n:
        songs_to_return = unrated_songs + random.sample(
            [s for s in all_songs if s.id in rated_song_ids],
            request.n - len(unrated_songs)
        )
    else:
        songs_to_return = random.sample(unrated_songs, request.n)
    
    return songs_to_return


@router.post("/answer", status_code=204)
def answer_quiz(request: QuizAnswerRequest, session: Session = Depends(get_session)):
    """Record user's like/dislike for a song."""
    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify song exists
    song = session.get(Song, request.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if feedback already exists
    existing = session.exec(
        select(UserSongFeedback).where(
            UserSongFeedback.user_id == request.user_id,
            UserSongFeedback.song_id == request.song_id
        )
    ).first()
    
    if existing:
        # Update existing feedback
        existing.liked = request.liked
        session.add(existing)
    else:
        # Create new feedback
        feedback = UserSongFeedback(
            user_id=request.user_id,
            song_id=request.song_id,
            liked=request.liked
        )
        session.add(feedback)
    
    session.commit()
    return Response(status_code=204)
