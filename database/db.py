import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

# Setup logger
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

def get_engine(db_uri=None):
    """Create and return an engine with suitable pool parameters."""
    if not db_uri:
        from config import get_config
        db_uri = get_config().SQLALCHEMY_DATABASE_URI
        
    engine_kwargs = {}
    if 'mysql' in db_uri:
        engine_kwargs = {
            'pool_recycle': 280,
            'pool_pre_ping': True
        }
    return create_engine(db_uri, **engine_kwargs)
