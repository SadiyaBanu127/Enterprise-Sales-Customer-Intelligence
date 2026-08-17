from datetime import datetime
from database.db import db

class Region(db.Model):
    __tablename__ = 'regions'

    region_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    country = db.Column(db.String(50), default='United States', nullable=False)
    market_tier = db.Column(db.String(20), default='Tier 1')
    target_growth_rate = db.Column(db.Numeric(5, 2), default=12.50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sales_reps = db.relationship('SalesRep', backref='region', lazy=True, cascade='all, delete-orphan')
    customers = db.relationship('Customer', backref='region', lazy=True)
    orders = db.relationship('Order', backref='region', lazy=True)

    def to_dict(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region_name,
            'country': self.country,
            'market_tier': self.market_tier,
            'target_growth_rate': float(self.target_growth_rate) if self.target_growth_rate is not None else 0.0,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

class SalesRep(db.Model):
    __tablename__ = 'sales_reps'

    rep_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rep_code = db.Column(db.String(20), unique=True, nullable=False)
    rep_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id', ondelete='CASCADE'), nullable=False, index=True)
    quota_annual = db.Column(db.Numeric(12, 2), default=500000.00, nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    orders = db.relationship('Order', backref='sales_rep', lazy=True)

    def to_dict(self):
        return {
            'rep_id': self.rep_id,
            'rep_code': self.rep_code,
            'rep_name': self.rep_name,
            'email': self.email,
            'region_id': self.region_id,
            'region_name': self.region.region_name if self.region else None,
            'quota_annual': float(self.quota_annual) if self.quota_annual is not None else 0.0,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'is_active': self.is_active
        }
