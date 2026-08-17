import os
import json
import logging
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from database.db import db
from models.customer import Customer
from models.analytics_models import PredictionAudit

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / 'services' / 'models_cache'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / 'churn_random_forest.joblib'
METRICS_FILE = MODEL_DIR / 'churn_model_metrics.json'

FEATURE_NAMES = [
    'recency_days',
    'total_orders_count',
    'total_spend',
    'average_order_value',
    'tenure_days',
    'recency_score',
    'frequency_score',
    'monetary_score'
]

def generate_customer_feature_dataframe():
    """Extracts customer features and derives a realistic churn target from historical activity."""
    customers = Customer.query.all()
    if not customers:
        return pd.DataFrame()

    ref_date = pd.to_datetime('2026-08-01')
    data = []

    for c in customers:
        signup_dt = pd.to_datetime(c.signup_date) if c.signup_date else pd.to_datetime('2023-01-01')
        tenure_days = max(1, (ref_date - signup_dt).days)
        recency = c.recency_days if c.recency_days is not None else 365
        orders = c.total_orders_count if c.total_orders_count is not None else 0
        spend = float(c.total_spend or 0.0)
        aov = float(c.average_order_value or 0.0)

        # Churn ground truth definition:
        # A customer is churned (1) if recency > 180 days or (recency > 120 days and order count <= 1)
        # Otherwise active (0)
        is_churned = 1 if (recency > 180 or (recency > 120 and orders <= 1)) else 0

        data.append({
            'customer_id': c.customer_id,
            'customer_code': c.customer_code,
            'recency_days': recency,
            'total_orders_count': orders,
            'total_spend': spend,
            'average_order_value': aov,
            'tenure_days': tenure_days,
            'recency_score': c.recency_score or 1,
            'frequency_score': c.frequency_score or 1,
            'monetary_score': c.monetary_score or 1,
            'churned': is_churned
        })

    return pd.DataFrame(data)

def train_churn_model():
    """Trains Random Forest & Gradient Boosting models on actual customer dataset."""
    print("[*] Training Customer Churn ML models on actual database records...")
    df = generate_customer_feature_dataframe()
    if df.empty or len(df) < 50:
        logger.warning("Not enough customer data to train ML model.")
        return None

    X = df[FEATURE_NAMES]
    y = df['churned']

    # Train / Test Split (80/20) with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )
    rf_model.fit(X_train, y_train)

    # Predictions & Probabilities on Test Set
    y_pred = rf_model.predict(X_test)
    y_prob = rf_model.predict_proba(X_test)[:, 1]

    # Calculate real evaluation metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))

    # Real Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = [int(val) for val in cm.ravel()]

    # ROC Curve coordinates for frontend plotting
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    # Downsample ROC curve for clean JSON serialization
    step = max(1, len(fpr) // 30)
    roc_data = {
        'fpr': [round(float(val), 4) for val in fpr[::step]],
        'tpr': [round(float(val), 4) for val in tpr[::step]]
    }

    # Feature Importances
    importances = rf_model.feature_importances_
    feat_imp = [
        {'feature': feat, 'importance': round(float(imp), 4)}
        for feat, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
    ]

    metrics = {
        'model_name': 'RandomForestClassifier (Enterprise v2.0)',
        'trained_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'dataset_size': len(df),
        'test_size': len(X_test),
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'confusion_matrix': {
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn,
            'true_positives': tp
        },
        'feature_importances': feat_imp,
        'roc_curve': roc_data
    }

    # Save model and metrics to disk
    joblib.dump(rf_model, MODEL_FILE)
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Batch score all customers in DB with real ML probabilities
    all_probs = rf_model.predict_proba(X)[:, 1]
    df['ml_churn_prob'] = all_probs

    mappings = []
    for idx, row in df.iterrows():
        prob = float(row['ml_churn_prob'])
        risk = 'High Risk' if prob >= 0.65 else ('Medium Risk' if prob >= 0.35 else 'Low Risk')
        mappings.append({
            'customer_id': int(row['customer_id']),
            'churn_risk_score': round(prob, 4),
            'churn_risk_level': risk
        })

    db.session.bulk_update_mappings(Customer, mappings)
    db.session.commit()
    print(f"[+] Churn ML model trained successfully. ROC-AUC: {roc_auc:.4f}, F1: {f1:.4f}")
    return metrics

def load_or_train_churn_model():
    """Loads cached churn model or trains a fresh one if missing."""
    if MODEL_FILE.exists() and METRICS_FILE.exists():
        try:
            model = joblib.load(MODEL_FILE)
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
            return model, metrics
        except Exception as e:
            logger.error(f"Error loading churn model: {e}")
    
    metrics = train_churn_model()
    model = joblib.load(MODEL_FILE) if MODEL_FILE.exists() else None
    return model, metrics

def get_churn_evaluation_data():
    """Returns the model evaluation metrics dictionary."""
    _, metrics = load_or_train_churn_model()
    return metrics or {}

def predict_single_customer(customer_id):
    """Generates real-time churn prediction, key risk drivers, and prescriptive recommendations for a customer."""
    cust = Customer.query.get(customer_id)
    if not cust:
        return {'success': False, 'error': 'Customer not found'}

    model, _ = load_or_train_churn_model()
    if not model:
        return {'success': False, 'error': 'Churn model is not available'}

    ref_date = pd.to_datetime('2026-08-01')
    signup_dt = pd.to_datetime(cust.signup_date) if cust.signup_date else pd.to_datetime('2023-01-01')
    tenure_days = max(1, (ref_date - signup_dt).days)

    features = pd.DataFrame([{
        'recency_days': cust.recency_days or 365,
        'total_orders_count': cust.total_orders_count or 0,
        'total_spend': float(cust.total_spend or 0.0),
        'average_order_value': float(cust.average_order_value or 0.0),
        'tenure_days': tenure_days,
        'recency_score': cust.recency_score or 1,
        'frequency_score': cust.frequency_score or 1,
        'monetary_score': cust.monetary_score or 1
    }])[FEATURE_NAMES]

    prob = float(model.predict_proba(features)[0, 1])
    risk_level = 'High Risk' if prob >= 0.65 else ('Medium Risk' if prob >= 0.35 else 'Low Risk')

    # Derive prescriptive recommendation
    if risk_level == 'High Risk':
        if cust.total_spend and float(cust.total_spend) > 5000:
            rec = "CRITICAL VIP INTERVENTION: Assign dedicated Customer Success Manager for an executive review call and propose tailored contract renewal incentives."
        elif cust.recency_days and cust.recency_days > 200:
            rec = "WIN-BACK CAMPAIGN: Trigger automated multi-touch win-back email sequence with a 20% reactivation promotion."
        else:
            rec = "RETENTION CAMPAIGN: Launch targeted survey to identify friction points and offer personalized product discounts."
    elif risk_level == 'Medium Risk':
        rec = "ENGAGEMENT OUTREACH: Share recent product updates, case studies, and invite to technical webinar."
    else:
        rec = "UP-SELL & NURTURE: Customer is healthy and active. Target for cross-selling complementary enterprise software modules."

    # Identify top risk drivers
    drivers = []
    if (cust.recency_days or 0) > 150:
        drivers.append(f"High inactivity period ({cust.recency_days} days since last purchase)")
    if (cust.total_orders_count or 0) <= 1:
        drivers.append("Single order history (low purchase frequency)")
    if (cust.frequency_score or 0) <= 2:
        drivers.append("Below-average order cadence")
    if not drivers:
        drivers.append("Stable transaction history and consistent engagement")

    # Audit log entry in DB
    audit = PredictionAudit(
        customer_id=cust.customer_id,
        model_name='RandomForestClassifier_v1',
        churn_probability=round(prob, 4),
        predicted_risk_level=risk_level,
        key_drivers=drivers,
        recommended_action=rec
    )
    db.session.add(audit)
    db.session.commit()

    return {
        'success': True,
        'customer_id': cust.customer_id,
        'customer_code': cust.customer_code,
        'customer_name': cust.customer_name,
        'segment': cust.segment,
        'churn_probability': round(prob * 100, 1),
        'churn_risk_level': risk_level,
        'key_drivers': drivers,
        'recommended_action': rec,
        'last_purchase_date': cust.last_purchase_date.strftime('%Y-%m-%d') if cust.last_purchase_date else 'N/A',
        'total_spend': float(cust.total_spend or 0.0),
        'total_orders': cust.total_orders_count or 0
    }

def get_churn_risk_overview():
    """Calculates customer counts grouped by Churn Risk Level."""
    total = Customer.query.count() or 1
    high_count = Customer.query.filter(Customer.churn_risk_level == 'High Risk').count()
    med_count = Customer.query.filter(Customer.churn_risk_level == 'Medium Risk').count()
    low_count = Customer.query.filter(Customer.churn_risk_level == 'Low Risk').count()

    return {
        'total_customers': total,
        'high_risk_count': high_count,
        'medium_risk_count': med_count,
        'low_risk_count': low_count,
        'high_risk_pct': round((high_count / total) * 100, 2),
        'medium_risk_pct': round((med_count / total) * 100, 2),
        'low_risk_pct': round((low_count / total) * 100, 2)
    }
