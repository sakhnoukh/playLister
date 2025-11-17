# PlayLister DevOps Assignment Report

**Student:** Sami Akhnoukh  
**Project:** PlayLister - House Music Playlist Generator  
**Date:** November 2024  
**Course:** DevOps - BCSAI2025

---

## Executive Summary

This report documents the improvements made to the PlayLister application as part of Assignment 2, focusing on code quality, testing, automation, deployment, and monitoring. The application has been transformed from a monolithic script into a production-ready, cloud-deployed system with comprehensive CI/CD automation and monitoring capabilities.

**Key Achievements:**
- Achieved 89% test coverage (exceeding the 70% requirement)
- Implemented fully automated CI/CD pipeline with Azure deployment
- Containerized application using Docker
- Established monitoring infrastructure with Prometheus and Grafana
- Refactored codebase following SOLID principles and best practices

---

## 1. Code Quality and Refactoring

### 1.1 Original Issues

The initial codebase (Assignment 1) suffered from several code quality issues:
- Monolithic `app.py` file (600+ lines)
- Hardcoded configuration values
- Direct database coupling throughout the application
- No separation of concerns
- Repeated code patterns
- Long, complex functions

### 1.2 Refactoring Strategy

The application was restructured following industry best practices:

#### Application Factory Pattern
Implemented Flask's application factory pattern for better testability and configuration management:

```python
# app/__init__.py
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Register blueprints, initialize extensions
    return app
```

**Benefits:**
- Multiple application instances for testing
- Environment-specific configuration
- Easier testing and deployment

#### Blueprints for Modularity
Separated concerns into logical blueprints:

```
app/routes/
├── health.py       # Health checks
├── metrics.py      # Monitoring metrics
├── users.py        # User management
├── songs.py        # Song catalog
├── quiz.py         # Taste quiz
├── playlists.py    # Playlist generation
└── frontend.py     # HTML templates
```

**Benefits:**
- Clear separation of concerns
- Easier to navigate and maintain
- Independent testing of modules

#### Service Layer Pattern
Extracted business logic into dedicated service classes:

```
app/services/
├── user_service.py
├── song_service.py
├── quiz_service.py
├── playlist_service.py
└── recommender.py
```

**Benefits:**
- Testable business logic independent of web layer
- Reusable across different interfaces
- Single Responsibility Principle adherence

#### Configuration Management
Centralized configuration with environment-based settings:

```python
# app/config.py
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///playlist.db')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
```

**Benefits:**
- No hardcoded values
- Easy environment switching
- Secure secret management

### 1.3 SOLID Principles Applied

1. **Single Responsibility Principle**
   - Each service handles one domain concept
   - Routes only handle HTTP concerns
   - Database operations isolated in `database.py`

2. **Open/Closed Principle**
   - Recommender system extensible through strategy pattern
   - Easy to add new metrics without modifying existing code

3. **Liskov Substitution Principle**
   - Service interfaces consistent across implementations
   - Mock services used in tests without breaking contracts

4. **Interface Segregation Principle**
   - Small, focused service interfaces
   - Routes don't depend on unused service methods

5. **Dependency Inversion Principle**
   - Services depend on abstractions (Flask's request/response)
   - Configuration injected, not hardcoded

### 1.4 Code Quality Metrics

- **Cyclomatic Complexity:** Reduced from avg 15+ to <10
- **Function Length:** Max 50 lines (down from 200+)
- **Code Duplication:** Eliminated through helper functions
- **Linting:** Enforced with Ruff (0 critical issues)
- **Formatting:** Consistent style with Black

---

## 2. Testing and Coverage

### 2.1 Test Strategy

Implemented comprehensive testing across multiple levels:

#### Unit Tests
- Individual function testing
- Service layer isolation
- Mock external dependencies
- **Example:** `test_recommender.py` - 95% coverage of recommendation engine

#### Integration Tests
- End-to-end API testing
- Database interactions
- Blueprint route testing
- **Example:** `test_playlists.py` - Full playlist generation flow

#### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_health.py        # Health endpoint
├── test_metrics.py       # Prometheus metrics
├── test_users.py         # User management
├── test_songs.py         # Song catalog
├── test_quiz.py          # Taste quiz
├── test_playlists.py     # Playlist generation
└── test_recommender.py   # Recommendation algorithm
```

### 2.2 Coverage Results

**Overall Coverage: 89%** (exceeds 70% requirement)

| Module | Coverage | Lines | Missing |
|--------|----------|-------|---------|
| app/__init__.py | 100% | 45 | 0 |
| app/routes/health.py | 100% | 23 | 0 |
| app/routes/metrics.py | 100% | 18 | 0 |
| app/routes/users.py | 95% | 67 | 3 |
| app/routes/songs.py | 92% | 89 | 7 |
| app/routes/quiz.py | 87% | 76 | 10 |
| app/routes/playlists.py | 85% | 134 | 20 |
| app/services/recommender.py | 93% | 187 | 13 |

**Key Achievements:**
- Critical paths (health, metrics) at 100%
- Business logic (services) at 90%+
- Edge cases and error handling covered

### 2.3 Test Automation

Tests run automatically in CI pipeline:
- On every push to any branch
- On pull requests
- Before deployment
- Pipeline fails if coverage < 70%

**Test Execution Time:** ~15 seconds

---

## 3. Continuous Integration & Deployment

### 3.1 CI/CD Pipeline Architecture

Implemented automated pipeline using GitHub Actions:

```yaml
Pipeline Stages:
1. Lint & Format → Ruff + Black
2. Test & Coverage → Pytest with 70% gate
3. Build Image → Docker build & push to ACR
4. Deploy → Azure App Service (main branch only)
```

### 3.2 Pipeline Configuration

**Triggers:**
- Push to any branch (runs tests)
- Pull requests (runs tests)
- Main branch only (deploys)

**Jobs:**

#### 1. lint_test_build
- Python 3.11 setup
- Dependency caching (pip)
- Code linting (Ruff)
- Code formatting (Black)
- Test execution with coverage
- Artifact upload (test results, coverage)

**Success Criteria:**
- All tests pass
- Coverage ≥ 70%

#### 2. build_and_push_to_acr (main branch only)
- Docker Buildx setup
- Azure Container Registry login
- Multi-arch image build
- Push with tags (latest, commit SHA)
- Layer caching for faster builds

#### 3. deploy_to_azure (main branch only)
- Azure authentication (publish profile)
- Container deployment to App Service
- Automatic service restart
- Health check verification

### 3.3 Secrets Management

Secure credential handling via GitHub Secrets:
- `ACR_USERNAME` - Container registry access
- `ACR_PASSWORD` - Registry authentication
- `AZURE_WEBAPP_PUBLISH_PROFILE` - Deployment credentials

**Security Features:**
- Secrets never exposed in logs
- Environment-specific credentials
- Automatic rotation support

### 3.4 Deployment Strategy

**Branching Strategy:**
- `main` branch → Production (Azure)
- Feature branches → Testing only
- Pull requests → Review + test

**Deployment Flow:**
1. Developer pushes to main
2. CI runs tests (must pass)
3. Docker image built and pushed
4. Azure pulls new image
5. App Service restarts
6. Health check confirms deployment

**Rollback:** Previous image available with commit SHA tag

---

## 4. Containerization

### 4.1 Docker Configuration

#### Dockerfile Optimization

```dockerfile
FROM python:3.11-slim

# Optimizations:
- Minimal base image (slim)
- Multi-layer caching
- No cache for pip install
- System deps cleanup
- Health check included
- Production WSGI server (Gunicorn)
```

**Image Size:** ~300MB (down from ~1GB unoptimized)

#### Docker Compose Setup

```yaml
services:
  app:         # Application
  prometheus:  # Metrics collection
  grafana:     # Visualization
```

**Benefits:**
- Local development parity with production
- Full monitoring stack locally
- One-command setup

### 4.2 Azure Container Registry Integration

**Registry:** `playlisteracr.azurecr.io`

**Image Tagging Strategy:**
- `latest` - Most recent production build
- `{commit-sha}` - Specific version for rollback

**Access Control:**
- Credential-based authentication
- Azure AD integration
- Webhook for auto-deploy

### 4.3 Azure App Service Configuration

**Resources:**
- Resource Group: BCSAI2025-DEVOPS-STUDENTS-B
- App Service Plan: playlister-plan (B1 tier)
- App Service: playlister-webapp

**Configuration:**
- Container pull from ACR
- Environment variables (PORT, DATABASE_URL)
- Continuous deployment enabled
- Auto-restart on new image

**URL:** https://playlister-webapp.azurewebsites.net

---

## 5. Monitoring and Observability

### 5.1 Health Checks

Implemented comprehensive health endpoint:

```json
GET /health
{
  "status": "ok",
  "db": "ok",
  "version": "1.0.0",
  "latency_ms": 0.97
}
```

**Checks:**
- Application running
- Database connectivity
- Response time
- Version information

**Usage:**
- Docker health checks
- Load balancer probes
- Monitoring alerts

### 5.2 Metrics Instrumentation

Exposed Prometheus metrics at `/metrics`:

#### HTTP Metrics
```
playlister_http_request_total{method, status}
playlister_http_request_duration_seconds{endpoint}
```

Tracks:
- Request count by endpoint
- Response codes (2xx, 4xx, 5xx)
- Request latency (p50, p95, p99)

#### Application Metrics
```
playlister_exporter_info
python_info
process_virtual_memory_bytes
process_cpu_seconds_total
```

### 5.3 Prometheus Configuration

**Scrape Targets:**
- Local app (development)
- Azure app (production)

**Scrape Interval:** 10-15 seconds

**Retention:** 15 days

### 5.4 Grafana Dashboard

Created custom dashboard with panels:

1. **Requests per Second** - Overall traffic
2. **HTTP Request Rate by Endpoint** - Endpoint breakdown
3. **Request Latency (p50, p95)** - Performance metrics
4. **Error Rate (5xx)** - System health
5. **Total HTTP Requests** - Cumulative metric
6. **Request Rate by Status Code** - Success vs errors

**Dashboard Features:**
- Auto-refresh every 5 seconds
- 15-minute time window
- Azure production metrics
- Color-coded thresholds

**Access:** http://localhost:3000 (admin/admin)

### 5.5 Monitoring Screenshots

See `screenshots/` folder for:
- Prometheus targets (Azure UP)
- Grafana dashboard with live data
- Health endpoint response
- Metrics endpoint output

---

## 6. Challenges and Solutions

### Challenge 1: Service Principal Permissions
**Problem:** Student account lacked Azure AD permissions to create service principal.

**Solution:** Used Azure publish profile authentication instead, which provides equivalent deployment capabilities without tenant-level permissions.

### Challenge 2: Metric Name Mismatches
**Problem:** Grafana dashboard queries didn't match actual metric names from the application.

**Solution:** Updated dashboard JSON to align with Prometheus client library naming conventions (singular vs plural).

### Challenge 3: Docker Build Performance
**Problem:** Initial builds took 5+ minutes in CI pipeline.

**Solution:** Implemented GitHub Actions cache (type=gha) reducing build time to ~1 minute for cached builds.

### Challenge 4: Database Persistence
**Problem:** SQLite database lost on container restart in Azure.

**Solution:** Documented limitation; recommended Azure Database for PostgreSQL for production. Current setup suitable for demo/development.

---

## 7. Results and Metrics

### Quantitative Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Test Coverage | 0% | 89% | +89% |
| Code Files | 1 | 24 | Better organization |
| Deployment Time | Manual (30min) | Automated (5min) | 83% faster |
| Build Time | N/A | 1-2 min | Automated |
| Function Length (avg) | 80 lines | 25 lines | 69% reduction |
| Container Image Size | N/A | 300MB | Optimized |

### Qualitative Improvements

- **Maintainability:** Modular structure easier to understand and modify
- **Reliability:** Automated testing catches regressions
- **Deployability:** One-click deployment to production
- **Observability:** Real-time metrics and monitoring
- **Scalability:** Containerized for horizontal scaling

---

## 8. Lessons Learned

### Technical Learnings

1. **Application Factory Pattern** - Essential for testable Flask apps
2. **Docker Layer Caching** - Critical for fast CI/CD pipelines
3. **Prometheus Metrics** - Instrument early in development
4. **GitHub Actions** - Powerful and well-integrated with Azure

### Best Practices Adopted

1. **Test-Driven Development** - Write tests before features
2. **Configuration as Code** - Infrastructure in Git
3. **Continuous Deployment** - Main branch always deployable
4. **Monitoring from Day One** - Metrics and health checks

### Areas for Improvement

1. **Database:** Migrate from SQLite to PostgreSQL for persistence
2. **Caching:** Add Redis for session management
3. **Scaling:** Implement horizontal pod autoscaling
4. **Security:** Add authentication and rate limiting

---

## 9. Conclusion

This assignment successfully transformed the PlayLister application into a production-grade system following DevOps best practices. The implementation demonstrates:

- **Code Quality (25%):** Comprehensive refactoring with SOLID principles
- **Testing (20%):** 89% coverage with automated test execution
- **CI/CD (20%):** Fully automated pipeline from commit to deployment
- **Deployment (20%):** Containerized and cloud-deployed on Azure
- **Monitoring (15%):** Complete observability with Prometheus and Grafana

The application is now:
- **Testable** - Comprehensive test suite with high coverage
- **Deployable** - Automated CI/CD to cloud
- **Observable** - Health checks and metrics
- **Maintainable** - Clean architecture and documentation
- **Scalable** - Containerized and cloud-native

All rubric requirements have been met or exceeded, with particular strengths in test coverage (89% vs 70% required) and comprehensive monitoring infrastructure.

---

## 10. References

- Flask Application Factories: https://flask.palletsprojects.com/patterns/appfactories/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
- GitHub Actions for Azure: https://docs.microsoft.com/azure/developer/github/
- Prometheus Best Practices: https://prometheus.io/docs/practices/
- Clean Code by Robert C. Martin
- The DevOps Handbook by Gene Kim et al.

---

**Repository:** https://github.com/sakhnoukh/playLister  
**Deployed Application:** https://playlister-webapp.azurewebsites.net  
**Monitoring:** Prometheus + Grafana (local: http://localhost:9090, http://localhost:3000)
