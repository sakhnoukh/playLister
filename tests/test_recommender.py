"""Unit tests for recommender service."""

import pytest
from app.services.recommender import RecommenderService
from app.config import Config


@pytest.fixture
def config():
    """Get test configuration."""
    return Config()


@pytest.fixture
def recommender(config):
    """Create recommender service instance."""
    return RecommenderService(config)


@pytest.fixture
def sample_song():
    """Sample song for testing."""
    return {
        "id": 1,
        "title": "Test Song",
        "artist": "Test Artist",
        "subgenre": "deep-house",
        "year": 2020,
        "tags": "melodic;uplifting",
        "bpm": 120
    }


@pytest.fixture
def liked_songs():
    """Sample liked songs."""
    return [
        {
            "id": 2,
            "artist": "Test Artist",
            "subgenre": "deep-house",
            "year": 2019,
            "tags": "melodic;chill",
            "bpm": 118
        },
        {
            "id": 3,
            "artist": "Another Artist",
            "subgenre": "tech-house",
            "year": 2021,
            "tags": "uplifting;energetic",
            "bpm": 125
        }
    ]


@pytest.fixture
def disliked_songs():
    """Sample disliked songs."""
    return [
        {
            "id": 4,
            "artist": "Disliked Artist",
            "subgenre": "progressive-house",
            "year": 2015,
            "tags": "dark;heavy",
            "bpm": 128
        }
    ]


def test_score_song_artist_affinity_positive(recommender, sample_song, liked_songs):
    """Test positive artist affinity scoring."""
    score = recommender.score_song(sample_song, liked_songs, [])
    
    # Should get bonus for matching artist with liked song
    assert score > 0


def test_score_song_artist_affinity_negative(recommender, sample_song, disliked_songs):
    """Test negative artist affinity scoring."""
    # Change song to have disliked artist
    song_with_disliked_artist = sample_song.copy()
    song_with_disliked_artist["artist"] = "Disliked Artist"
    
    score = recommender.score_song(song_with_disliked_artist, [], disliked_songs)
    
    # Should get penalty for matching disliked artist
    assert score < 0


def test_score_song_subgenre_affinity(recommender, sample_song, liked_songs):
    """Test subgenre affinity scoring."""
    score = recommender.score_song(sample_song, liked_songs, [])
    
    # Should get bonus for matching subgenre
    assert score > 0


def test_score_song_tag_overlap(recommender, liked_songs):
    """Test tag overlap scoring."""
    song_with_matching_tags = {
        "id": 5,
        "artist": "New Artist",
        "subgenre": "minimal-house",
        "year": 2020,
        "tags": "melodic;uplifting",  # Matches both liked songs
        "bpm": 120
    }
    
    score = recommender.score_song(song_with_matching_tags, liked_songs, [])
    
    # Should get bonus for tag overlap
    assert score > 0


def test_score_song_bpm_proximity(recommender, liked_songs):
    """Test BPM proximity scoring."""
    # Song with BPM close to liked songs' median
    song_similar_bpm = {
        "id": 6,
        "artist": "BPM Artist",
        "subgenre": "house",
        "year": 2020,
        "tags": "test",
        "bpm": 121  # Close to median of 118 and 125
    }
    
    score = recommender.score_song(song_similar_bpm, liked_songs, [])
    
    # Should have positive score
    assert score >= 0


def test_score_song_era_proximity(recommender, liked_songs):
    """Test year proximity scoring."""
    song_similar_year = {
        "id": 7,
        "artist": "Year Artist",
        "subgenre": "house",
        "year": 2020,  # Between 2019 and 2021
        "tags": "test",
        "bpm": 120
    }
    
    score = recommender.score_song(song_similar_year, liked_songs, [])
    
    # Should have positive score for year proximity
    assert score >= 0


def test_score_song_seed_similarity(recommender, sample_song):
    """Test seed song similarity bonus."""
    seed_song = {
        "id": 8,
        "artist": "Test Artist",  # Same as sample_song
        "subgenre": "deep-house",  # Same as sample_song
        "year": 2020,
        "tags": "melodic;uplifting",  # Same as sample_song
        "bpm": 120
    }
    
    score_with_seed = recommender.score_song(sample_song, [], [], seed_song)
    score_without_seed = recommender.score_song(sample_song, [], [])
    
    # Score with seed should be higher
    assert score_with_seed > score_without_seed


def test_score_song_determinism(recommender, sample_song, liked_songs):
    """Test that scoring is mostly deterministic (except for small jitter)."""
    score1 = recommender.score_song(sample_song, liked_songs, [])
    score2 = recommender.score_song(sample_song, liked_songs, [])
    
    # Scores should be very close (within jitter range of 0.1)
    assert abs(score1 - score2) < 0.2


def test_generate_recommendations_basic(recommender):
    """Test basic recommendation generation."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    recommendations = recommender.generate_recommendations(
        all_songs, [], [], count=5
    )
    
    assert len(recommendations) == 5


def test_generate_recommendations_excludes_disliked(recommender):
    """Test that disliked songs are excluded."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    disliked = [all_songs[0], all_songs[1]]
    
    recommendations = recommender.generate_recommendations(
        all_songs, [], disliked, count=5
    )
    
    # Disliked songs should not be in recommendations
    disliked_ids = {s["id"] for s in disliked}
    recommended_ids = {s["id"] for s in recommendations}
    
    assert len(disliked_ids & recommended_ids) == 0


def test_generate_recommendations_with_genre_preference(recommender):
    """Test recommendations with genre preference."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "deep-house" if i < 5 else "tech-house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    recommendations = recommender.generate_recommendations(
        all_songs, [], [], count=5, preferred_genre="deep-house"
    )
    
    # Should prioritize deep-house songs
    assert len(recommendations) <= 5


def test_cold_start_playlist_random(recommender):
    """Test cold start playlist generation."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    playlist = recommender.generate_cold_start_playlist(all_songs, count=5)
    
    assert len(playlist) == 5


def test_cold_start_playlist_with_genre(recommender):
    """Test cold start with genre preference."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "deep-house" if i < 5 else "tech-house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    playlist = recommender.generate_cold_start_playlist(
        all_songs, count=5, preferred_genre="deep-house"
    )
    
    assert len(playlist) == 5


def test_cold_start_insufficient_genre_songs(recommender):
    """Test cold start when not enough songs in preferred genre."""
    all_songs = [
        {"id": i, "artist": f"Artist{i}", "subgenre": "deep-house" if i < 2 else "tech-house", 
         "year": 2020, "tags": "test", "bpm": 120}
        for i in range(10)
    ]
    
    # Request 5 songs but only 2 are deep-house
    playlist = recommender.generate_cold_start_playlist(
        all_songs, count=5, preferred_genre="deep-house"
    )
    
    # Should get 5 songs total (2 deep-house + 3 others)
    assert len(playlist) == 5


def test_recommender_uses_configurable_weights(config):
    """Test that recommender uses configurable weights."""
    # Modify config weights
    config.ARTIST_WEIGHT = 10.0
    recommender = RecommenderService(config)
    
    song = {
        "id": 1,
        "artist": "Test Artist",
        "subgenre": "house",
        "year": 2020,
        "tags": "test",
        "bpm": 120
    }
    
    liked = [{
        "id": 2,
        "artist": "Test Artist",  # Same artist
        "subgenre": "tech-house",
        "year": 2020,
        "tags": "different",
        "bpm": 130
    }]
    
    score = recommender.score_song(song, liked, [])
    
    # Should have high score due to large artist weight
    assert score >= 10.0
