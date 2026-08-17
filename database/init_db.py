import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask
from config import get_config
from database.db import db
from models.user import User
from models.region import Region, SalesRep
from models.product import Category, Product
from models.customer import Customer
from models.order import Order, OrderItem
from models.analytics_models import PredictionAudit, ForecastCache

def init_database(app=None):
    """Initializes the database schema and seeds default administrative accounts."""
    created_app = False
    if app is None:
        created_app = True
        app = Flask(__name__)
        app.config.from_object(get_config())
        
        # Ensure data folder exists
        (BASE_DIR / 'data' / 'raw').mkdir(parents=True, exist_ok=True)
        (BASE_DIR / 'data' / 'processed').mkdir(parents=True, exist_ok=True)
        (BASE_DIR / 'services' / 'models_cache').mkdir(parents=True, exist_ok=True)
        (BASE_DIR / 'reports').mkdir(parents=True, exist_ok=True)

        db.init_app(app)

    with app.app_context():
        print(f"[*] Initializing database with URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Create all tables defined in models
        db.create_all()
        print("[+] Database tables created successfully.")

        # Seed default users if they don't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@enterprise.com',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            print("[+] Seeded default Admin user (username: admin / pass: Admin@123)")

        analyst = User.query.filter_by(username='analyst').first()
        if not analyst:
            analyst = User(
                username='analyst',
                email='analyst@enterprise.com',
                full_name='Senior Lead Analyst',
                role='analyst',
                is_active=True
            )
            analyst.set_password('Analyst@123')
            db.session.add(analyst)
            print("[+] Seeded default Analyst user (username: analyst / pass: Analyst@123)")

        # Seed base regions if none exist
        if Region.query.count() == 0:
            regions_data = [
                Region(region_id=1, region_name='North America - East', country='United States', market_tier='Tier 1', target_growth_rate=14.50),
                Region(region_id=2, region_name='North America - West', country='United States', market_tier='Tier 1', target_growth_rate=18.00),
                Region(region_id=3, region_name='North America - Central', country='United States', market_tier='Tier 2', target_growth_rate=11.00),
                Region(region_id=4, region_name='North America - South', country='United States', market_tier='Tier 2', target_growth_rate=15.20)
            ]
            db.session.add_all(regions_data)
            print("[+] Seeded 4 base geographic regions.")

        # Seed base categories if none exist
        if Category.query.count() == 0:
            cats = [
                Category(category_id=1, category_name='Enterprise Cloud Software', description='SaaS subscriptions, enterprise licenses, AI developer seats', target_margin=78.50),
                Category(category_id=2, category_name='Hardware & Servers', description='Rackmount servers, edge compute units, high-performance switches', target_margin=32.00),
                Category(category_id=3, category_name='Professional Services', description='Implementation consulting, data migration, security audits', target_margin=55.00),
                Category(category_id=4, category_name='Cybersecurity Solutions', description='Endpoint protection, SIEM infrastructure, zero-trust gateways', target_margin=68.00),
                Category(category_id=5, category_name='Data & AI Infrastructure', description='Vector DB appliances, GPU clusters, data lakehouse integrations', target_margin=48.00)
            ]
            db.session.add_all(cats)
            print("[+] Seeded 5 product categories.")

        db.session.commit()
        print("[+] Database initialization and base seeding completed successfully.")

if __name__ == '__main__':
    init_database()
