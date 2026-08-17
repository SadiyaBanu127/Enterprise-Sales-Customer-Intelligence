import logging
from sqlalchemy import func
from database.db import db
from models.order import Order

logger = logging.getLogger(__name__)

def simulate_business_scenario(price_change_pct=0.0, discount_change_pct=0.0, quantity_change_pct=0.0, marketing_spend=0.0):
    """Simulates the financial impact of pricing, discount, volume, and marketing budget adjustments."""
    # Retrieve current baseline annual financial metrics (last 12 months or total dataset)
    baseline_q = db.session.query(
        func.sum(Order.subtotal_amount).label('baseline_subtotal'),
        func.sum(Order.discount_amount).label('baseline_discount'),
        func.sum(Order.total_amount).label('baseline_revenue'),
        func.sum(Order.total_cost).label('baseline_cost'),
        func.sum(Order.net_profit).label('baseline_profit'),
        func.count(Order.order_id).label('baseline_orders')
    ).filter(Order.status != 'Cancelled').first()

    base_subtotal = float(baseline_q[0] or 1000000.0)
    base_discount = float(baseline_q[1] or 50000.0)
    base_revenue = float(baseline_q[2] or 1000000.0)
    base_cost = float(baseline_q[3] or 600000.0)
    base_profit = float(baseline_q[4] or 400000.0)
    base_orders = int(baseline_q[5] or 10000)
    base_margin = round((base_profit / base_revenue) * 100, 2) if base_revenue > 0 else 0.0

    # Simulation multipliers
    price_factor = 1.0 + (price_change_pct / 100.0)
    volume_factor = 1.0 + (quantity_change_pct / 100.0)
    
    # Marketing impact: Every $10,000 in marketing can yield ~1.5% incremental volume lift
    marketing_volume_lift = (marketing_spend / 10000.0) * 0.015
    effective_volume_factor = volume_factor + marketing_volume_lift

    # Simulated gross subtotal (affected by price and volume)
    simulated_subtotal = base_subtotal * price_factor * effective_volume_factor

    # Simulated discount (discount rate altered by discount_change_pct)
    base_discount_rate = (base_discount / base_subtotal) if base_subtotal > 0 else 0.05
    new_discount_rate = max(0.0, min(0.50, base_discount_rate + (discount_change_pct / 100.0)))
    simulated_discount = simulated_subtotal * new_discount_rate

    # Simulated net revenue
    simulated_revenue = simulated_subtotal - simulated_discount

    # Simulated Cost of Goods Sold (COGS scales with volume, not price)
    simulated_cogs = base_cost * effective_volume_factor
    simulated_total_cost = simulated_cogs + marketing_spend

    # Simulated profit and margin
    simulated_profit = simulated_revenue - simulated_total_cost
    simulated_margin = round((simulated_profit / simulated_revenue) * 100, 2) if simulated_revenue > 0 else 0.0

    # Variances
    revenue_delta = simulated_revenue - base_revenue
    revenue_delta_pct = round((revenue_delta / base_revenue) * 100, 2) if base_revenue > 0 else 0.0

    profit_delta = simulated_profit - base_profit
    profit_delta_pct = round((profit_delta / base_profit) * 100, 2) if base_profit > 0 else 0.0

    margin_delta = round(simulated_margin - base_margin, 2)

    # Marketing ROI
    marketing_roi = round((profit_delta / marketing_spend) * 100, 2) if marketing_spend > 0 else 0.0

    # Strategic business interpretation
    if profit_delta > 0:
        recommendation = f"Favorable scenario! This combination generates an estimated +${profit_delta:,.2f} (+{profit_delta_pct}%) in net profit and expands operating margin by {margin_delta:+.2f}%."
    else:
        recommendation = f"Caution: This scenario dilutes net profit by -${abs(profit_delta):,.2f} ({profit_delta_pct}%). Consider tightening discount allowances or increasing target unit pricing to preserve margin."

    return {
        'inputs': {
            'price_change_pct': price_change_pct,
            'discount_change_pct': discount_change_pct,
            'quantity_change_pct': quantity_change_pct,
            'marketing_spend': marketing_spend
        },
        'baseline': {
            'revenue': round(base_revenue, 2),
            'cost': round(base_cost, 2),
            'profit': round(base_profit, 2),
            'margin_pct': base_margin,
            'orders_count': base_orders
        },
        'simulated': {
            'revenue': round(simulated_revenue, 2),
            'cost': round(simulated_total_cost, 2),
            'profit': round(simulated_profit, 2),
            'margin_pct': simulated_margin
        },
        'variance': {
            'revenue_delta': round(revenue_delta, 2),
            'revenue_delta_pct': revenue_delta_pct,
            'profit_delta': round(profit_delta, 2),
            'profit_delta_pct': profit_delta_pct,
            'margin_delta_pct': margin_delta,
            'marketing_roi_pct': marketing_roi
        },
        'recommendation': recommendation
    }
