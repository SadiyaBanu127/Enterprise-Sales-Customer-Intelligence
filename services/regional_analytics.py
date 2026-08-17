import logging
from sqlalchemy import func
from database.db import db
from models.region import Region, SalesRep
from models.order import Order
from models.customer import Customer

logger = logging.getLogger(__name__)

def get_regional_intelligence():
    """Computes comprehensive regional performance, rankings, and growth trends."""
    regions = Region.query.all()
    if not regions:
        return {'regions': [], 'standouts': {}}

    regional_data = []
    
    # Calculate global totals for market share calculation
    total_sales_global = db.session.query(func.sum(Order.total_amount))\
        .filter(Order.status != 'Cancelled').scalar() or 1.0

    for r in regions:
        orders_q = db.session.query(
            func.sum(Order.total_amount).label('revenue'),
            func.sum(Order.total_cost).label('cost'),
            func.sum(Order.net_profit).label('profit'),
            func.count(Order.order_id).label('order_count'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(Order.region_id == r.region_id, Order.status != 'Cancelled').first()

        cust_count = Customer.query.filter_by(region_id=r.region_id).count()
        rep_count = SalesRep.query.filter_by(region_id=r.region_id).count()

        rev = round(float(orders_q[0] or 0.0), 2)
        cost = round(float(orders_q[1] or 0.0), 2)
        prof = round(float(orders_q[2] or 0.0), 2)
        orders = int(orders_q[3] or 0)
        aov = round(float(orders_q[4] or 0.0), 2)
        margin = round((prof / rev) * 100, 2) if rev > 0 else 0.0
        market_share = round((rev / float(total_sales_global)) * 100, 2)

        # Recent 90-day growth estimate vs prior 90-day
        recent_90 = db.session.query(func.sum(Order.total_amount))\
            .filter(Order.region_id == r.region_id, Order.order_date >= '2026-05-01', Order.status != 'Cancelled').scalar() or 0.0
        prior_90 = db.session.query(func.sum(Order.total_amount))\
            .filter(Order.region_id == r.region_id, Order.order_date >= '2026-02-01', Order.order_date < '2026-05-01', Order.status != 'Cancelled').scalar() or 1.0
        
        growth_rate = round(((float(recent_90) - float(prior_90)) / float(prior_90)) * 100, 2) if prior_90 > 0 else 0.0

        regional_data.append({
            'region_id': r.region_id,
            'region_name': r.region_name,
            'country': r.country,
            'market_tier': r.market_tier,
            'target_growth_rate': float(r.target_growth_rate or 12.0),
            'customer_count': cust_count,
            'rep_count': rep_count,
            'total_revenue': rev,
            'total_profit': prof,
            'total_cost': cost,
            'total_orders': orders,
            'average_order_value': aov,
            'profit_margin_pct': margin,
            'market_share_pct': market_share,
            'recent_growth_rate': growth_rate
        })

    # Sort to determine rankings
    by_rev = sorted(regional_data, key=lambda x: x['total_revenue'], reverse=True)
    by_growth = sorted(regional_data, key=lambda x: x['recent_growth_rate'], reverse=True)

    best_performing = by_rev[0] if by_rev else None
    worst_performing = by_rev[-1] if by_rev else None
    fastest_growing = by_growth[0] if by_growth else None
    declining_region = by_growth[-1] if by_growth else None

    return {
        'regional_breakdown': regional_data,
        'standouts': {
            'best_performing': best_performing,
            'worst_performing': worst_performing,
            'fastest_growing': fastest_growing,
            'declining_region': declining_region
        }
    }
