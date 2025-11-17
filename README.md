# 🎵 PlayLister - House Music Playlist Generator

[![CI](https://github.com/sakhnoukh/playLister/actions/workflows/ci.yml/badge.svg)](https://github.com/sakhnoukh/playLister/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen)](https://github.com/sakhnoukh/playLister)

A production-ready, retro-styled music playlist generator focused on house music, built with Flask and featuring a taste quiz system that learns your preferences to create personalized playlists. The application has a 90s-inspired retro UI design.

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

### 🚀 DevOps Features (Assignment 2)

- **Health & Metrics**: `/health` endpoint with DB checks and `/metrics` endpoint for Prometheus
- **Testing**: Comprehensive test suite with 89% coverage (≥70% enforced in CI)
- **CI/CD Pipeline**: Automated linting, testing, Docker builds, and deployment via GitHub Actions
- **Containerization**: Docker + docker-compose with Prometheus & Grafana monitoring stack
- **Code Quality**: App factory pattern, blueprints, services layer, configurable via environment variables

## 🛠 Tech Stack

- **Backend**: Flask (Python) with app factory pattern
- **Database**: SQLite with native Python connections
- **Frontend**: Vanilla HTML/CSS/JavaScript with retro styling
- **Server**: Gunicorn (production), Flask dev server (development)
- **Testing**: Pytest with pytest-cov (89% coverage)
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + Docker Compose
- **Code Quality**: Black, Ruff, MyPy

## 📦 Project Structure

```
playLister/
├── app/
│   ├── __init__.py         # App factory
│   ├── config.py           # Configuration management
│   ├── database.py         # Database utilities
│   ├── routes/             # Blueprint routes
│   │   ├── health.py       # Health check endpoint
│   │   ├── metrics.py      # Prometheus metrics
│   │   ├── users.py        # User routes
│   │   ├── songs.py        # Song routes
│   │   ├── quiz.py         # Quiz routes
│   │   ├── playlists.py    # Playlist routes
│   │   └── frontend.py     # HTML template routes
│   ├── services/           # Business logic layer
│   │   ├── user_service.py
│   │   ├── song_service.py
│   │   ├── quiz_service.py
│   │   ├── playlist_service.py
│   │   └── recommender.py  # Recommendation engine
│   ├── static/             # CSS and assets
│   └── templates/          # HTML templates
├── tests/                  # Test suite (89% coverage)
├── docker/                 # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── grafana-*/          # Grafana config
├── .github/workflows/      # CI/CD pipeline
│   └── ci.yml
├── seed/
│   └── house_tracks.csv    # 97 real house tracks
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Tool configuration
├── REPORT.md               # DevOps assignment report
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose (for containerized deployment)
- pip package manager

### Installation & Running

#### Development Mode

```bash
# Clone repository
git clone https://github.com/sakhnoukh/playLister.git
cd playLister

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Initialize database (automatic on first run)
python3 -c "from app.database import init_db; init_db()"

# Run development server
export FLASK_ENV=development
flask --app "app:create_app()" run --host=0.0.0.0 --port=8000

# Access at http://localhost:8000
```

#### Production Mode with Docker

```bash
# Build and run with monitoring stack
cd docker
docker-compose up --build

# Access services:
# - App: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

## 📊 Database

The application uses SQLite with the following schema:

- **users**: User profiles
- **songs**: House music catalog (50+ tracks)
- **user_song_feedback**: Quiz responses (likes/dislikes)
- **playlists**: Saved playlists
- **playlist_songs**: Playlist-song associations with ordering

The database is automatically created and seeded on first run from `seed/house_seed.csv`.

## 🎯 API Endpoints

### Health & Monitoring
- `GET /health` - Health check with DB status
- `GET /metrics` - Prometheus metrics

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
# Run all tests
pytest -v

# Run with coverage (≥70% enforced)
pytest --cov=app --cov-report=term-missing --cov-fail-under=70

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## 🔍 Code Quality

```bash
# Format code
black app tests

# Lint code
ruff check app tests

# Type checking (optional)
mypy app
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

## 📊 Monitoring

When running with docker-compose, you get a full monitoring stack:

- **Prometheus** (http://localhost:9090): Scrapes `/metrics` endpoint every 10s
- **Grafana** (http://localhost:3000): Visualize metrics with pre-configured dashboards
  - Default login: `admin` / `admin`
  - Prometheus datasource pre-configured

### Available Metrics

- `playlister_http_requests_total` - Total HTTP requests by endpoint, method, status
- `playlister_http_request_latency_seconds` - Request latency histogram
- `playlister_playlist_generate_total` - Playlist generation counter with success/genre labels
- Standard Python/Flask metrics (memory, CPU, etc.)

## 🚢 CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Lint & Format**: Runs ruff and black on every push
2. **Test**: Executes pytest with coverage gate (≥70%)
3. **Build & Push**: Builds Docker image and pushes to Azure Container Registry
4. **Deploy**: Automatically deploys to Azure App Service on `main` branch

### Azure Deployment

The application is configured for deployment to Azure:
- **Azure Container Registry**: `playlisteracr.azurecr.io`
- **App Service**: `playlister-webapp`
- **Resource Group**: `BCSAI2025-DEVOPS-STUDENTS-B`

**📖 See [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md) for complete setup instructions**

### Required GitHub Secrets

Add these secrets in GitHub Settings → Secrets → Actions:
- `ACR_USERNAME` - Azure Container Registry username
- `ACR_PASSWORD` - Azure Container Registry password
- `AZURE_CREDENTIALS` - Azure service principal credentials (JSON)

## 🔮 Future Enhancements

- User authentication with OAuth
- Multi-genre support beyond house music
- Advanced collaborative filtering
- Export playlists to M3U format
- Spotify/Apple Music integration
- Horizontal scaling with Redis session store
- PostgreSQL for production database

## 📄 License

MIT License - feel free to use this project for learning and development.

## 👤 Author

Built as part of a software development lifecycle course project.

## 🙏 Acknowledgments

- House music data curated from classic and modern tracks
- Retro UI inspired by 90s web design aesthetic
- FastAPI framework for excellent developer experience
