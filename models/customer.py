from datetime import datetime
from database.db import db

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(120), nullable=True)
    segment = db.Column(db.String(50), default='Standard', index=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id', ondelete='RESTRICT'), nullable=False, index=True)
    signup_date = db.Column(db.Date, nullable=False)
    
    # Aggregated metrics
    total_orders_count = db.Column(db.Integer, default=0)
    total_spend = db.Column(db.Numeric(12, 2), default=0.00)
    average_order_value = db.Column(db.Numeric(10, 2), default=0.00)
    last_purchase_date = db.Column(db.Date, nullable=True)
    
    # RFM Metrics
    recency_days = db.Column(db.Integer, default=0)
    recency_score = db.Column(db.Integer, default=1)
    frequency_score = db.Column(db.Integer, default=1)
    monetary_score = db.Column(db.Integer, default=1)
    rfm_score = db.Column(db.Integer, default=111, index=True)
    
    # Churn Metrics
    churn_risk_score = db.Column(db.Numeric(5, 4), default=0.0000)
    churn_risk_level = db.Column(db.String(20), default='Low Risk', index=True) # 'Low Risk', 'Medium Risk', 'High Risk'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('PredictionAudit', backref='customer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'customer_code': self.customer_code,
            'customer_name': self.customer_name,
            'email': self.email,
            'company_name': self.company_name,
            'segment': self.segment,
            'region_id': self.region_id,
            'region_name': self.region.region_name if self.region else None,
            'signup_date': self.signup_date.strftime('%Y-%m-%d') if self.signup_date else None,
            'total_orders_count': self.total_orders_count or 0,
            'total_spend': float(self.total_spend) if self.total_spend is not None else 0.0,
            'average_order_value': float(self.average_order_value) if self.average_order_value is not None else 0.0,
            'last_purchase_date': self.last_purchase_date.strftime('%Y-%m-%d') if self.last_purchase_date else None,
            'recency_days': self.recency_days or 0,
            'rfm_score': self.rfm_score,
            'recency_score': self.recency_score,
            'frequency_score': self.frequency_score,
            'monetary_score': self.monetary_score,
            'churn_risk_score': float(self.churn_risk_score) if self.churn_risk_score is not None else 0.0,
            'churn_risk_level': self.churn_risk_level or 'Low Risk',
            'is_active': self.is_active
        }
