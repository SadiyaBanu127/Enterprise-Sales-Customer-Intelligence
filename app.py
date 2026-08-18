import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from config import get_config
from database.db import db
from models.user import User

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('sales_intelligence')

def create_app(config_class=None):
    """Application factory for Enterprise Sales & Customer Intelligence Platform."""
    app = Flask(__name__)
    
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize Database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.analytics import analytics_bp
    from routes.prediction import prediction_bp
    from routes.etl_routes import etl_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(etl_bp)
    app.register_blueprint(reports_bp)

    # Ensure every supported production/development launch path (including
    # ``flask run``) has the schema and documented demo accounts available.
    # Previously this ran only in the ``__main__`` block, so launching through
    # the Flask CLI could render the login page before its users table/accounts
    # had been created.  Tests retain control of their isolated database setup.
    if not app.config.get('TESTING'):
        from database.init_db import init_database
        init_database(app)

    # Global Context Processor
    @app.context_processor
    def inject_global_vars():
        from flask_login import current_user
        return {
            'app_name': 'Enterprise Sales Intelligence',
            'current_year': 2026,
            'current_user': current_user
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_message="Page Not Found (404)"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal Server Error: {e}")
        return render_template('base.html', error_message="Internal Server Error (500)"), 500

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template('base.html', error_message="Access Forbidden (403): You do not have permission."), 403

    return app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"🚀 Enterprise Sales & Customer Intelligence Platform")
    print(f"🌐 Server running at: http://{host}:{port}/")
    print(f"🔑 Default Admin:    admin / Admin@123")
    print(f"📊 Default Analyst:  analyst / Analyst@123")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=True)
