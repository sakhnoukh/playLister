"""Metrics initialization and custom metrics."""

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, CollectorRegistry, REGISTRY

# Module-level metrics instance
metrics = None

# Custom metrics
playlist_generate_total = None


def init_metrics(app):
    """Initialize Prometheus metrics for the Flask app."""
    global metrics, playlist_generate_total
    
    # Only initialize if not already initialized or if in test mode
    if app.config.get("TESTING"):
        # Use a separate registry for tests
        registry = CollectorRegistry()
        metrics = PrometheusMetrics(app, registry=registry, defaults_prefix="playlister")
    else:
        if metrics is None:
            metrics = PrometheusMetrics(app, defaults_prefix="playlister")
        else:
            # Already initialized, skip
            return metrics
    
    # App info metric
    try:
        metrics.info(
            "app_info", 
            "Application info", 
            version=app.config.get("APP_VERSION", "0.0.0")
        )
    except ValueError:
        # Metric already exists, skip
        pass
    
    # Custom metric for playlist generation
    if playlist_generate_total is None:
        try:
            playlist_generate_total = Counter(
                'playlister_playlist_generate_total',
                'Total playlist generation requests',
                ['success', 'genre'],
                registry=registry if app.config.get("TESTING") else REGISTRY
            )
        except ValueError:
            # Metric already exists, skip
            pass
    
    return metrics
