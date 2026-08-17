import logging
from flask import Blueprint, render_template, request, jsonify
from services.auth_service import login_required_view, login_required_api
from services.churn_model import (
    get_churn_evaluation_data,
    get_churn_risk_overview,
    predict_single_customer,
    train_churn_model
)
from services.forecasting import get_forecast_results, generate_forecast_models
from services.what_if import simulate_business_scenario

logger = logging.getLogger(__name__)
prediction_bp = Blueprint('prediction', __name__)

# --- VIEW ROUTES ---

@prediction_bp.route('/churn')
@login_required_view
def churn_view():
    """Renders Customer Churn ML Prediction dashboard."""
    return render_template('churn.html', active_page='churn')

@prediction_bp.route('/forecast')
@login_required_view
def forecast_view():
    """Renders Time-Series Sales Forecast view."""
    return render_template('forecast.html', active_page='forecast')

@prediction_bp.route('/what-if')
@login_required_view
def what_if_view():
    """Renders Interactive What-If Financial Scenario Simulator."""
    return render_template('what_if.html', active_page='what-if')

# --- REST API ENDPOINTS ---

@prediction_bp.route('/api/churn/overview', methods=['GET'])
@login_required_api
def api_churn_overview():
    """Returns Churn ML model evaluation metrics (ROC-AUC, Confusion Matrix) and risk level overview."""
    metrics = get_churn_evaluation_data()
    risk_overview = get_churn_risk_overview()
    return jsonify({
        'success': True,
        'metrics': metrics,
        'risk_overview': risk_overview
    })

@prediction_bp.route('/api/churn/predict/<int:customer_id>', methods=['GET'])
@login_required_api
def api_predict_customer(customer_id):
    """Computes live single-customer churn risk and recommendations."""
    res = predict_single_customer(customer_id)
    return jsonify(res)

@prediction_bp.route('/api/churn/retrain', methods=['POST'])
@login_required_api
def api_retrain_churn():
    """Triggers ML model retraining on current database state."""
    metrics = train_churn_model()
    return jsonify({
        'success': True,
        'message': 'Churn model retrained successfully',
        'metrics': metrics
    })

@prediction_bp.route('/api/forecast', methods=['GET'])
@login_required_api
def api_forecast():
    """Returns time series forecast for specified horizon (30, 90, 180 days)."""
    horizon = int(request.args.get('horizon', 90))
    data = get_forecast_results(horizon_days=horizon)
    return jsonify({
        'success': True,
        'data': data
    })

@prediction_bp.route('/api/what-if', methods=['GET', 'POST'])
@login_required_api
def api_what_if():
    """Simulates financial outcomes based on adjusted price, discount, volume, and marketing."""
    if request.method == 'POST':
        body = request.get_json() or {}
        price = float(body.get('price_change_pct', 0.0))
        discount = float(body.get('discount_change_pct', 0.0))
        qty = float(body.get('quantity_change_pct', 0.0))
        marketing = float(body.get('marketing_spend', 0.0))
    else:
        price = float(request.args.get('price_change_pct', 0.0))
        discount = float(request.args.get('discount_change_pct', 0.0))
        qty = float(request.args.get('quantity_change_pct', 0.0))
        marketing = float(request.args.get('marketing_spend', 0.0))

    result = simulate_business_scenario(
        price_change_pct=price,
        discount_change_pct=discount,
        quantity_change_pct=qty,
        marketing_spend=marketing
    )
    return jsonify({
        'success': True,
        'scenario': result
    })
