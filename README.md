# 🎵 PlayLister - House Music Playlist Generator

A retro-styled music playlist generator focused on house music, built with Flask and featuring a taste quiz system that learns your preferences to create personalized playlists. The application has a 90s-inspired retro UI design.

## ✨ Features

- **User Profiles**: Simple name-based user system (no authentication in v1)
- **Taste Quiz**: Like/dislike random songs to build your taste profile
- **Smart Playlist Generation**: Content-based recommendation algorithm using:
  - Artist affinity scoring
  - Subgenre matching
  - Tag overlap analysis
  - BPM and era proximity
  - Optional seed song similarity
- **Playlist Management**: Save, view, and delete your custom playlists
- **Retro UI**: 90s dot-com era aesthetic with pixel fonts and classic styling

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with native Python connections
- **Frontend**: Vanilla HTML/CSS/JavaScript with retro styling
- **Server**: Flask development server
- **Testing**: Pytest

## 📦 Project Structure

```
playLister/
├── app/
│   ├── static/
│   │   └── retro.css        # Retro styling
│   └── templates/           # HTML templates
│       ├── home.html
│       ├── quiz.html
│       ├── generate.html
│       └── profile.html
├── app.py                 # Flask application with all routes
├── run.sh                 # Startup script
├── seed/
│   └── house_tracks.csv       # 97 real house tracks
├── report/
│   └── report.md           # Project report
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation & Running

**Method 1: Using the run script**

```bash
git clone https://github.com/sakhnoukh/playLister.git
cd playLister
chmod +x run.sh
./run.sh
```

**Method 2: Manual setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/sakhnoukh/playLister.git
   cd playLister
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:8080`

## 📊 Database

The application uses SQLite with the following schema:

- **users**: User profiles
- **songs**: House music catalog (50+ tracks)
- **user_song_feedback**: Quiz responses (likes/dislikes)
- **playlists**: Saved playlists
- **playlist_songs**: Playlist-song associations with ordering

The database is automatically created and seeded on first run from `seed/house_seed.csv`.

## 🎯 API Endpoints

### Users
- `POST /api/users` - Create or get user by name

### Songs
- `GET /api/songs` - List songs with search/filter

### Quiz
- `POST /api/quiz/start` - Get random songs for quiz
- `POST /api/quiz/answer` - Submit like/dislike

### Playlists
- `POST /api/playlists/generate` - Generate playlist preview
- `POST /api/playlists` - Save playlist
- `GET /api/playlists?user_id={id}` - List user's playlists
- `GET /api/playlists/{id}` - Get playlist details
- `DELETE /api/playlists/{id}` - Delete playlist

### Example: Generate a playlist
```bash
curl -X POST "http://localhost:8080/api/playlists/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "count": 20,
    "genre": "deep-house"
  }'
```

## 🧪 Running Tests

```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## 🎨 Recommendation Algorithm

The playlist generator uses a weighted scoring system:

- **Artist affinity**: ±2 points (liked/disliked)
- **Subgenre affinity**: ±1 points (liked/disliked)
- **Tag overlap**: +0.5 per shared tag
- **BPM proximity**: +0.3 if within ±8 BPM of user's median
- **Era proximity**: +0.2 if within ±5 years of user's median
- **Seed song similarity**: Additional bonuses for matching attributes

Songs are ranked by score and top N are returned, excluding any previously disliked tracks.

## 📝 Code Quality

Format code:
```bash
black app/ tests/
```

Lint code:
```bash
ruff check app/ tests/
```

## 🔮 Future Enhancements

- User authentication with OAuth
- Multi-genre support beyond house music
- Advanced collaborative filtering
- Export playlists to M3U format
- Spotify/Apple Music integration
- Dockerization for easy deployment
- CI/CD pipeline with GitHub Actions

## 📄 License

MIT License - feel free to use this project for learning and development.

## 👤 Author

Built as part of a software development lifecycle course project.

## 🙏 Acknowledgments

- House music data curated from classic and modern tracks
- Retro UI inspired by 90s web design aesthetic
- FastAPI framework for excellent developer experience
