import os
import sys
import logging
from pathlib import Path

from flask import Flask, render_template, jsonify
from flask_login import LoginManager

from config import get_config
from database.db import db
from models.user import User


# ============================================================
# Configure Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("sales_intelligence")


# ============================================================
# Application Factory
# ============================================================

def create_app(config_class=None):
    """Application factory for Enterprise Sales & Customer Intelligence Platform."""

    app = Flask(__name__)

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    if config_class is None:
        config_class = get_config()

    app.config.from_object(config_class)

    # --------------------------------------------------------
    # Initialize Database
    # --------------------------------------------------------

    db.init_app(app)

    # --------------------------------------------------------
    # Initialize Flask-Login
    # --------------------------------------------------------

    login_manager = LoginManager()

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # --------------------------------------------------------
    # Register Blueprints
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Initialize Database
    # --------------------------------------------------------

    if not app.config.get("TESTING"):

        from database.init_db import init_database

        try:
            init_database(app)
            logger.info("Database initialization completed.")
        except Exception as e:
            logger.exception(
                "Database initialization failed: %s",
                e
            )

    # --------------------------------------------------------
    # Global Context Processor
    # --------------------------------------------------------

    @app.context_processor
    def inject_global_vars():

        from flask_login import current_user

        return {
            "app_name": "Enterprise Sales Intelligence",
            "current_year": 2026,
            "current_user": current_user
        }

    # --------------------------------------------------------
    # Error Handlers
    # --------------------------------------------------------

    @app.errorhandler(404)
    def page_not_found(e):
        return (
            render_template(
                "base.html",
                error_message="Page Not Found (404)"
            ),
            404
        )

    @app.errorhandler(500)
    def internal_server_error(e):

        logger.error(
            "Internal Server Error: %s",
            e
        )

        return (
            render_template(
                "base.html",
                error_message="Internal Server Error (500)"
            ),
            500
        )

    @app.errorhandler(403)
    def access_forbidden(e):

        return (
            render_template(
                "base.html",
                error_message=(
                    "Access Forbidden (403): "
                    "You do not have permission."
                )
            ),
            403
        )

    return app


# ============================================================
# Create Flask Application
# ============================================================

app = create_app()


# ============================================================
# Run Application
# ============================================================

if __name__ == "__main__":

    host = os.environ.get(
        "HOST",
        "127.0.0.1"
    )

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    print("\n=======================================================")
    print("🚀 Enterprise Sales & Customer Intelligence Platform")
    print(f"🌐 Server running at: http://{host}:{port}/")
    print("🔑 Default Admin:    admin / Admin@123")
    print("📊 Default Analyst:  analyst / Analyst@123")
    print("=======================================================\n")

    # Important:
    # use_reloader=False prevents the Windows/Flask
    # signal error when the application is launched normally.

    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False
    )