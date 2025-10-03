"""Database initialization and seeding."""

import csv
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Song

# Database URL - SQLite in the project root
DATABASE_URL = "sqlite:///./playlist.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session


def seed_songs():
    """Load songs from CSV seed file."""
    seed_file = Path(__file__).parent.parent / "seed" / "house_seed.csv"
    
    with Session(engine) as session:
        # Check if songs already exist
        existing_count = session.exec(select(Song)).first()
        if existing_count:
            print("Songs already seeded, skipping...")
            return
        
        # Load from CSV
        with open(seed_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            songs = []
            for row in reader:
                song = Song(
                    title=row["title"],
                    artist=row["artist"],
                    subgenre=row["subgenre"],
                    year=int(row["year"]),
                    tags=row["tags"],
                    bpm=int(row["bpm"]) if row["bpm"] else None,
                )
                songs.append(song)
            
            session.add_all(songs)
            session.commit()
            print(f"Seeded {len(songs)} songs from {seed_file}")
