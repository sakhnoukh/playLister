"""Configuration management for PlayLister app."""

import os
from typing import Optional


class Config:
    """Base configuration."""
    
    # App
    APP_NAME: str = os.environ.get("APP_NAME", "PlayLister")
    APP_VERSION: str = os.environ.get("APP_VERSION", "1.0.0")
    APP_ENV: str = os.environ.get("APP_ENV", "development")
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///playlist.db")
    
    # Server
    HOST: str = os.environ.get("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", os.environ.get("FLASK_PORT", "8000")))
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    # Recommender weights (configurable)
    ARTIST_WEIGHT: float = float(os.environ.get("ARTIST_WEIGHT", "2.0"))
    SUBGENRE_WEIGHT: float = float(os.environ.get("SUBGENRE_WEIGHT", "1.0"))
    TAG_WEIGHT: float = float(os.environ.get("TAG_WEIGHT", "0.5"))
    BPM_WEIGHT: float = float(os.environ.get("BPM_WEIGHT", "0.3"))
    ERA_WEIGHT: float = float(os.environ.get("ERA_WEIGHT", "0.2"))
    SEED_ARTIST_WEIGHT: float = float(os.environ.get("SEED_ARTIST_WEIGHT", "1.0"))
    SEED_SUBGENRE_WEIGHT: float = float(os.environ.get("SEED_SUBGENRE_WEIGHT", "1.0"))
    SEED_TAG_WEIGHT: float = float(os.environ.get("SEED_TAG_WEIGHT", "1.0"))
    SEED_BPM_WEIGHT: float = float(os.environ.get("SEED_BPM_WEIGHT", "0.3"))
    GENRE_BONUS: float = float(os.environ.get("GENRE_BONUS", "5.0"))
    
    # Tolerances
    BPM_TOLERANCE: int = int(os.environ.get("BPM_TOLERANCE", "8"))
    YEAR_TOLERANCE: int = int(os.environ.get("YEAR_TOLERANCE", "5"))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration object by name."""
    if config_name is None:
        config_name = os.environ.get("APP_ENV", "default")
    return config_map.get(config_name, DevelopmentConfig)
