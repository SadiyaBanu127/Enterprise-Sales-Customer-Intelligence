from datetime import datetime
from database.db import db

class PredictionAudit(db.Model):
    __tablename__ = 'predictions'

    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False, index=True)
    model_name = db.Column(db.String(80), default='RandomForestClassifier_v1', nullable=False)
    churn_probability = db.Column(db.Numeric(5, 4), nullable=False)
    predicted_risk_level = db.Column(db.String(20), nullable=False, index=True)
    key_drivers = db.Column(db.JSON, nullable=True)
    recommended_action = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'prediction_id': self.prediction_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.customer_name if self.customer else None,
            'model_name': self.model_name,
            'churn_probability': float(self.churn_probability) if self.churn_probability is not None else 0.0,
            'predicted_risk_level': self.predicted_risk_level,
            'key_drivers': self.key_drivers,
            'recommended_action': self.recommended_action,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class ForecastCache(db.Model):
    __tablename__ = 'forecasts'

    forecast_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    forecast_date = db.Column(db.Date, nullable=False, index=True)
    horizon_days = db.Column(db.Integer, nullable=False, index=True) # 30, 90, 180
    model_type = db.Column(db.String(50), default='HoltWinters_Additive', nullable=False)
    predicted_revenue = db.Column(db.Numeric(14, 2), nullable=False)
    lower_ci_95 = db.Column(db.Numeric(14, 2), nullable=False)
    upper_ci_95 = db.Column(db.Numeric(14, 2), nullable=False)
    growth_rate_pct = db.Column(db.Numeric(6, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'forecast_id': self.forecast_id,
            'forecast_date': self.forecast_date.strftime('%Y-%m-%d') if self.forecast_date else None,
            'horizon_days': self.horizon_days,
            'model_type': self.model_type,
            'predicted_revenue': float(self.predicted_revenue) if self.predicted_revenue is not None else 0.0,
            'lower_ci_95': float(self.lower_ci_95) if self.lower_ci_95 is not None else 0.0,
            'upper_ci_95': float(self.upper_ci_95) if self.upper_ci_95 is not None else 0.0,
            'growth_rate_pct': float(self.growth_rate_pct) if self.growth_rate_pct is not None else 0.0
        }
