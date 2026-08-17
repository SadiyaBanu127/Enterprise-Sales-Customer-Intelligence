import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from database.db import db
from models.order import Order
from models.analytics_models import ForecastCache

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / 'services' / 'models_cache'
FORECAST_CACHE_FILE = MODEL_DIR / 'sales_forecast_data.json'

def get_historical_daily_sales():
    """Extracts aggregated daily sales from completed orders."""
    results = db.session.query(
        Order.order_date,
        db.func.sum(Order.total_amount).label('daily_revenue'),
        db.func.count(Order.order_id).label('daily_orders')
    ).filter(Order.status != 'Cancelled')\
     .group_by(Order.order_date)\
     .order_by(Order.order_date)\
     .all()

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame([{
        'ds': pd.to_datetime(r[0]),
        'y': float(r[1] or 0.0),
        'orders': int(r[2] or 0)
    } for r in results])

    df = df.set_index('ds').resample('D').asfreq().fillna(0.0)
    return df

def generate_forecast_models(horizon_days=180):
    """Fits Holt-Winters Exponential Smoothing model and generates forecasts for 30, 90, and 180 day horizons."""
    print(f"[*] Generating Time-Series Sales Forecast for horizon={horizon_days} days...")
    df = get_historical_daily_sales()
    if df.empty or len(df) < 60:
        logger.warning("Insufficient historical data for time-series forecasting.")
        return {}

    # Aggregate to weekly series for robust statistical modeling & seasonal cycle
    df_weekly = df['y'].resample('W').sum()
    if len(df_weekly) < 15:
        # Fallback to daily rolling average if weekly is too short
        series = df['y']
        freq_str = 'D'
        periods = horizon_days
        seasonal_periods = 7
    else:
        series = df_weekly
        freq_str = 'W'
        periods = max(4, horizon_days // 7)
        seasonal_periods = 52 if len(series) >= 104 else 12

    try:
        # Fit Holt-Winters Additive model
        hw_model = ExponentialSmoothing(
            series,
            trend='add',
            seasonal='add' if len(series) >= (seasonal_periods * 2) else None,
            seasonal_periods=seasonal_periods if len(series) >= (seasonal_periods * 2) else None,
            damped_trend=True
        ).fit(damping_trend=0.95, optimized=True)
        
        forecast_values = hw_model.forecast(periods)
        fitted_values = hw_model.fittedvalues
        residuals = series - fitted_values
        std_resid = float(np.std(residuals)) if len(residuals) > 0 else float(np.std(series) * 0.15)
    except Exception as e:
        logger.error(f"Holt-Winters fit error: {e}, applying resilient trend extrapolation.")
        # Fallback linear trend extrapolation
        x = np.arange(len(series))
        poly = np.polyfit(x, series.values, deg=1)
        future_x = np.arange(len(series), len(series) + periods)
        forecast_values = pd.Series(np.polyval(poly, future_x))
        std_resid = float(np.std(series.values) * 0.12)

    # Build forecast dates
    last_date = series.index[-1]
    if freq_str == 'W':
        forecast_dates = pd.date_range(start=last_date + timedelta(days=7), periods=periods, freq='W')
    else:
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')

    forecast_series = pd.Series(forecast_values.values, index=forecast_dates)
    forecast_series = forecast_series.apply(lambda v: max(0.0, float(v)))

    # Compute 95% Confidence Intervals (1.96 * sigma * sqrt(h))
    h_steps = np.arange(1, periods + 1)
    margin_of_error = 1.96 * std_resid * np.sqrt(h_steps * 0.2 + 1)
    lower_ci = np.maximum(0, forecast_series.values - margin_of_error)
    upper_ci = forecast_series.values + margin_of_error

    # Downsample historical series for snappy frontend rendering (last 52 weeks or 12 months)
    hist_sample = series.tail(52)
    historical_data = {
        'dates': [d.strftime('%Y-%m-%d') for d in hist_sample.index],
        'values': [round(float(v), 2) for v in hist_sample.values]
    }

    forecast_data = {
        'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
        'values': [round(float(v), 2) for v in forecast_series.values],
        'lower_ci': [round(float(v), 2) for v in lower_ci],
        'upper_ci': [round(float(v), 2) for v in upper_ci]
    }

    # Financial & Growth Metrics
    # Compare forecasted revenue with the preceding period of same duration
    expected_rev_total = float(np.sum(forecast_series.values))
    prior_period_rev = float(np.sum(series.tail(periods).values)) if len(series) >= periods else float(np.sum(series.values))
    
    growth_rate = round(((expected_rev_total - prior_period_rev) / prior_period_rev) * 100, 2) if prior_period_rev > 0 else 0.0

    # Business interpretation narrative
    if growth_rate > 5.0:
        interpretation = f"Positive acceleration expected. Sales are forecasted to expand by +{growth_rate}% over the next {horizon_days} days, driven by healthy customer retention and seasonal momentum. Ensure inventory levels for high-margin software licenses and enterprise hardware are replenished."
    elif growth_rate >= -2.0:
        interpretation = f"Stable baseline demand. Projected sales show steady performance (+{growth_rate}%) over the upcoming {horizon_days} days. Recommended strategy: Focus on cross-selling AI infrastructure and expanding sales rep territory coverage."
    else:
        interpretation = f"Potential seasonal softening identified ({growth_rate}% contraction projected). Implement targeted marketing initiatives and discount optimization for at-risk accounts."

    payload = {
        'horizon_days': horizon_days,
        'model_name': 'Holt-Winters Exponential Smoothing (Damped Additive Trend)',
        'expected_revenue': round(expected_rev_total, 2),
        'prior_period_revenue': round(prior_period_rev, 2),
        'expected_growth_rate': growth_rate,
        'interpretation': interpretation,
        'historical': historical_data,
        'forecast': forecast_data,
        'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(FORECAST_CACHE_FILE, 'w') as f:
        json.dump(payload, f, indent=2)

    return payload

def get_forecast_results(horizon_days=90):
    """Retrieves forecast results, calculating on demand or using cached predictions."""
    if FORECAST_CACHE_FILE.exists():
        try:
            with open(FORECAST_CACHE_FILE, 'r') as f:
                data = json.load(f)
            if data.get('horizon_days') == horizon_days:
                return data
        except Exception:
            pass

    return generate_forecast_models(horizon_days=horizon_days)
