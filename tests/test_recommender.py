"""Recommender system tests."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.models import User, Song, UserSongFeedback
from app.services.recommender import PlaylistRecommender


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Add test songs
        songs = [
            Song(title="Song 1", artist="Artist A", subgenre="house", year=2000, tags="vocal;piano", bpm=120),
            Song(title="Song 2", artist="Artist A", subgenre="deep-house", year=2001, tags="deep;vocal", bpm=122),
            Song(title="Song 3", artist="Artist B", subgenre="house", year=2002, tags="piano;classic", bpm=124),
            Song(title="Song 4", artist="Artist B", subgenre="tech-house", year=2003, tags="club", bpm=126),
            Song(title="Song 5", artist="Artist C", subgenre="french-house", year=2004, tags="filter;classic", bpm=123),
        ]
        for song in songs:
            session.add(song)
        session.commit()
        
        yield session


def test_random_playlist_no_feedback(session: Session):
    """Test that recommender returns random songs when no feedback exists."""
    user = User(name="TestUser")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    recommender = PlaylistRecommender(session)
    playlist = recommender.generate_playlist(user_id=user.id, count=3)
    
    assert len(playlist) == 3
    assert all(isinstance(song, Song) for song in playlist)


def test_playlist_excludes_disliked(session: Session):
    """Test that generated playlist excludes disliked songs."""
    user = User(name="TestUser")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Get first song and dislike it
    songs = session.query(Song).all()
    disliked_song = songs[0]
    
    feedback = UserSongFeedback(user_id=user.id, song_id=disliked_song.id, liked=False)
    session.add(feedback)
    session.commit()
    
    recommender = PlaylistRecommender(session)
    playlist = recommender.generate_playlist(user_id=user.id, count=5)
    
    # Check that disliked song is not in playlist
    playlist_ids = [song.id for song in playlist]
    assert disliked_song.id not in playlist_ids


def test_playlist_count(session: Session):
    """Test that generated playlist has the correct count."""
    user = User(name="TestUser")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    recommender = PlaylistRecommender(session)
    
    for count in [3, 5, 10]:
        playlist = recommender.generate_playlist(user_id=user.id, count=count)
        # Should return requested count or all available songs if less
        assert len(playlist) <= count


def test_playlist_no_duplicates(session: Session):
    """Test that generated playlist has no duplicate songs."""
    user = User(name="TestUser")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    recommender = PlaylistRecommender(session)
    playlist = recommender.generate_playlist(user_id=user.id, count=5)
    
    song_ids = [song.id for song in playlist]
    assert len(song_ids) == len(set(song_ids)), "Playlist contains duplicates"
