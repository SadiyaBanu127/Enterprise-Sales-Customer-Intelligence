from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.prediction import prediction_bp
from routes.etl_routes import etl_bp
from routes.reports import reports_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'analytics_bp',
    'prediction_bp',
    'etl_bp',
    'reports_bp'
]
