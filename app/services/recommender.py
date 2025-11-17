"""Recommendation service for playlist generation."""

import random
from typing import List, Dict, Any, Optional, Set

from ..config import Config


class RecommenderService:
    """Service for generating song recommendations based on user taste."""
    
    def __init__(self, config: Config):
        """Initialize recommender with configuration."""
        self.config = config
    
    def score_song(
        self,
        song: Dict[str, Any],
        liked_songs: List[Dict[str, Any]],
        disliked_songs: List[Dict[str, Any]],
        seed_song: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate recommendation score for a song.
        
        Args:
            song: Song to score
            liked_songs: List of songs the user liked
            disliked_songs: List of songs the user disliked
            seed_song: Optional seed song for similarity bonus
            
        Returns:
            Score value (higher is better)
        """
        score = 0.0
        
        # Artist affinity
        for liked in liked_songs:
            if song["artist"] == liked["artist"]:
                score += self.config.ARTIST_WEIGHT
        
        for disliked in disliked_songs:
            if song["artist"] == disliked["artist"]:
                score -= self.config.ARTIST_WEIGHT
        
        # Subgenre affinity
        for liked in liked_songs:
            if song["subgenre"] == liked["subgenre"]:
                score += self.config.SUBGENRE_WEIGHT
        
        for disliked in disliked_songs:
            if song["subgenre"] == disliked["subgenre"]:
                score -= self.config.SUBGENRE_WEIGHT
        
        # Tag overlap with liked songs
        song_tags = set(song["tags"].split(';')) if song["tags"] else set()
        for liked in liked_songs:
            liked_tags = set(liked["tags"].split(';')) if liked["tags"] else set()
            overlap = song_tags & liked_tags
            score += len(overlap) * self.config.TAG_WEIGHT
        
        # BPM proximity
        if song["bpm"] and liked_songs:
            liked_bpms = [s["bpm"] for s in liked_songs if s["bpm"]]
            if liked_bpms:
                median_bpm = sum(liked_bpms) / len(liked_bpms)
                if abs(song["bpm"] - median_bpm) <= self.config.BPM_TOLERANCE:
                    score += self.config.BPM_WEIGHT
        
        # Era proximity
        if liked_songs:
            liked_years = [s["year"] for s in liked_songs]
            median_year = sum(liked_years) / len(liked_years)
            if abs(song["year"] - median_year) <= self.config.YEAR_TOLERANCE:
                score += self.config.ERA_WEIGHT
        
        # Seed song similarity
        if seed_song:
            if song["artist"] == seed_song["artist"]:
                score += self.config.SEED_ARTIST_WEIGHT
            if song["subgenre"] == seed_song["subgenre"]:
                score += self.config.SEED_SUBGENRE_WEIGHT
            
            seed_tags = set(seed_song["tags"].split(';')) if seed_song["tags"] else set()
            tag_overlap = song_tags & seed_tags
            score += len(tag_overlap) * self.config.SEED_TAG_WEIGHT
            
            if song["bpm"] and seed_song["bpm"] and abs(song["bpm"] - seed_song["bpm"]) <= self.config.BPM_TOLERANCE:
                score += self.config.SEED_BPM_WEIGHT
        
        # Add small random jitter to avoid ties
        score += random.uniform(0, 0.1)
        
        return score
    
    def generate_recommendations(
        self,
        all_songs: List[Dict[str, Any]],
        liked_songs: List[Dict[str, Any]],
        disliked_songs: List[Dict[str, Any]],
        count: int,
        preferred_genre: Optional[str] = None,
        seed_song: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate song recommendations.
        
        Args:
            all_songs: All available songs
            liked_songs: Songs user liked
            disliked_songs: Songs user disliked
            count: Number of recommendations to generate
            preferred_genre: Optional genre filter
            seed_song: Optional seed song for similarity
            
        Returns:
            List of recommended songs
        """
        disliked_song_ids: Set[int] = {song["id"] for song in disliked_songs}
        
        # Filter songs by genre if specified
        if preferred_genre:
            genre_songs = [s for s in all_songs if s["subgenre"] == preferred_genre]
        else:
            genre_songs = []
        
        # Score each song
        scored_songs = []
        
        # First, process songs from the preferred genre if specified
        if preferred_genre and genre_songs:
            for song in genre_songs:
                if song["id"] in disliked_song_ids:
                    continue
                
                # Give a genre bonus to preferred genre songs
                score = self.score_song(song, liked_songs, disliked_songs, seed_song)
                score += self.config.GENRE_BONUS
                scored_songs.append((song, score))
        
        # Then process all songs to fill the playlist if needed
        for song in all_songs:
            # Skip songs that are already scored or disliked
            if song["id"] in disliked_song_ids or any(s["id"] == song["id"] for s, _ in scored_songs):
                continue
            
            score = self.score_song(song, liked_songs, disliked_songs, seed_song)
            scored_songs.append((song, score))
        
        # Sort by score and return top N
        scored_songs.sort(key=lambda x: x[1], reverse=True)
        result = [song for song, _ in scored_songs[:count]]
        
        return result
    
    def generate_cold_start_playlist(
        self,
        all_songs: List[Dict[str, Any]],
        count: int,
        preferred_genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate playlist for users without feedback (cold start).
        
        Args:
            all_songs: All available songs
            count: Number of songs to return
            preferred_genre: Optional genre filter
            
        Returns:
            List of songs
        """
        if preferred_genre:
            genre_songs = [s for s in all_songs if s["subgenre"] == preferred_genre]
            
            # If we have enough songs in the preferred genre
            if len(genre_songs) >= count:
                return random.sample(genre_songs, count)
            
            # Otherwise create a mixed playlist
            result = genre_songs.copy()
            remaining_songs = [song for song in all_songs if song not in result]
            needed = count - len(result)
            
            if needed > 0 and remaining_songs:
                result.extend(random.sample(remaining_songs, min(needed, len(remaining_songs))))
            
            return result
        
        # No genre preference - return random songs
        return random.sample(all_songs, min(count, len(all_songs)))
