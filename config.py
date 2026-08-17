import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'enterprise_sales_intelligence_secret_key_2026')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    # Database Settings
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'sales_intelligence_db')
    
    db_file_path = (BASE_DIR / 'data' / 'sales_intelligence.db').resolve().as_posix()
    # Priority: explicit DATABASE_URL -> constructed MySQL URL -> SQLite fallback
    _env_db_url = os.environ.get('DATABASE_URL')
    if _env_db_url and not _env_db_url.startswith('sqlite:///data'):
        SQLALCHEMY_DATABASE_URI = _env_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file_path}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    } if 'mysql' in SQLALCHEMY_DATABASE_URI else {}
    
    # File Paths
    DATA_RAW_DIR = BASE_DIR / 'data' / 'raw'
    DATA_PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
    MODELS_DIR = BASE_DIR / 'services' / 'models_cache'
    REPORTS_DIR = BASE_DIR / 'reports'
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'raw'
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload limit

    # Ensure directories exist
    (BASE_DIR / 'data' / 'raw').mkdir(parents=True, exist_ok=True)
    (BASE_DIR / 'data' / 'processed').mkdir(parents=True, exist_ok=True)
    (BASE_DIR / 'services' / 'models_cache').mkdir(parents=True, exist_ok=True)
    (BASE_DIR / 'reports').mkdir(parents=True, exist_ok=True)
    
    # ML & BI Defaults
    CHURN_THRESHOLD = float(os.environ.get('CHURN_THRESHOLD', 0.5))
    FORECAST_HORIZON_DAYS = int(os.environ.get('FORECAST_HORIZON_DAYS', 180))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
