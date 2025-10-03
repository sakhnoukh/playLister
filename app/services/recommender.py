"""Playlist recommendation engine using content-based filtering."""

import random
from statistics import median
from sqlmodel import Session, select
from app.models import Song, UserSongFeedback


class PlaylistRecommender:
    """Generate playlists based on user taste profile."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def generate_playlist(
        self,
        user_id: int,
        count: int,
        genre: str | None = None,
        seed_song_id: int | None = None
    ) -> list[Song]:
        """
        Generate a playlist based on user's taste profile.
        
        Args:
            user_id: User ID
            count: Number of songs to generate
            genre: Optional subgenre filter
            seed_song_id: Optional seed song for similarity
        
        Returns:
            List of Song objects ordered by score (descending)
        """
        # Get user's feedback
        feedbacks = self.session.exec(
            select(UserSongFeedback).where(UserSongFeedback.user_id == user_id)
        ).all()
        
        if not feedbacks:
            # No feedback yet - return random songs
            return self._random_playlist(count, genre)
        
        # Build taste profile
        liked_songs = []
        disliked_songs = []
        
        for feedback in feedbacks:
            song = self.session.get(Song, feedback.song_id)
            if feedback.liked:
                liked_songs.append(song)
            else:
                disliked_songs.append(song)
        
        # Get seed song if specified
        seed_song = None
        if seed_song_id:
            seed_song = self.session.get(Song, seed_song_id)
        
        # Get all candidate songs
        statement = select(Song)
        if genre:
            statement = statement.where(Song.subgenre == genre)
        
        all_songs = self.session.exec(statement).all()
        
        # Score each song
        scored_songs = []
        disliked_song_ids = {s.id for s in disliked_songs}
        
        for song in all_songs:
            # Skip songs user disliked
            if song.id in disliked_song_ids:
                continue
            
            score = self._score_song(song, liked_songs, disliked_songs, seed_song)
            scored_songs.append((song, score))
        
        # Sort by score and return top N
        scored_songs.sort(key=lambda x: x[1], reverse=True)
        return [song for song, score in scored_songs[:count]]
    
    def _score_song(
        self,
        song: Song,
        liked_songs: list[Song],
        disliked_songs: list[Song],
        seed_song: Song | None
    ) -> float:
        """
        Calculate recommendation score for a song.
        
        Scoring weights:
        - Artist affinity: +2 if liked, -2 if disliked
        - Subgenre affinity: +1 if liked, -1 if disliked
        - Tag overlap: +0.5 per shared tag
        - BPM proximity: +0.3 if within ±8 BPM of median
        - Era proximity: +0.2 if within ±5 years of median
        - Seed similarity: +1 per match (artist, subgenre, tags), +0.3 if BPM close
        """
        score = 0.0
        
        # Artist affinity
        for liked in liked_songs:
            if song.artist == liked.artist:
                score += 2.0
        
        for disliked in disliked_songs:
            if song.artist == disliked.artist:
                score -= 2.0
        
        # Subgenre affinity
        for liked in liked_songs:
            if song.subgenre == liked.subgenre:
                score += 1.0
        
        for disliked in disliked_songs:
            if song.subgenre == disliked.subgenre:
                score -= 1.0
        
        # Tag overlap with liked songs
        song_tags = set(song.tags.split(';')) if song.tags else set()
        for liked in liked_songs:
            liked_tags = set(liked.tags.split(';')) if liked.tags else set()
            overlap = song_tags & liked_tags
            score += len(overlap) * 0.5
        
        # BPM proximity
        if song.bpm and liked_songs:
            liked_bpms = [s.bpm for s in liked_songs if s.bpm]
            if liked_bpms:
                median_bpm = median(liked_bpms)
                if abs(song.bpm - median_bpm) <= 8:
                    score += 0.3
        
        # Era proximity
        if liked_songs:
            liked_years = [s.year for s in liked_songs]
            median_year = median(liked_years)
            if abs(song.year - median_year) <= 5:
                score += 0.2
        
        # Seed song similarity
        if seed_song:
            if song.artist == seed_song.artist:
                score += 1.0
            if song.subgenre == seed_song.subgenre:
                score += 1.0
            
            seed_tags = set(seed_song.tags.split(';')) if seed_song.tags else set()
            tag_overlap = song_tags & seed_tags
            score += len(tag_overlap) * 1.0
            
            if song.bpm and seed_song.bpm and abs(song.bpm - seed_song.bpm) <= 8:
                score += 0.3
        
        # Add small random jitter to avoid ties
        score += random.uniform(0, 0.1)
        
        return score
    
    def _random_playlist(self, count: int, genre: str | None = None) -> list[Song]:
        """Generate a random playlist (fallback when no feedback)."""
        statement = select(Song)
        if genre:
            statement = statement.where(Song.subgenre == genre)
        
        all_songs = self.session.exec(statement).all()
        
        if len(all_songs) <= count:
            return all_songs
        
        return random.sample(all_songs, count)


# Get the session from dependency injection
session = None


def get_recommender(session: Session) -> PlaylistRecommender:
    """Dependency injection for recommender."""
    return PlaylistRecommender(session)
