import logging
from sqlalchemy import func
from database.db import db
from models.product import Product, Category
from models.order import Order, OrderItem

logger = logging.getLogger(__name__)

def get_product_analytics_summary():
    """Computes comprehensive product performance, return rates, and profitability matrix."""
    query = db.session.query(
        Product.product_id,
        Product.product_sku,
        Product.product_name,
        Category.category_name,
        Product.unit_cost,
        Product.unit_price,
        func.sum(OrderItem.quantity).label('total_units_sold'),
        func.sum(OrderItem.item_total_amount).label('total_revenue'),
        func.sum(OrderItem.item_profit).label('total_profit'),
        func.avg(OrderItem.discount_pct).label('avg_discount'),
        func.count(OrderItem.item_id).label('total_order_lines'),
        func.sum(db.case((OrderItem.is_returned == True, 1), else_=0)).label('returned_lines')
    ).join(Category, Product.category_id == Category.category_id)\
     .join(OrderItem, Product.product_id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.order_id)\
     .filter(Order.status != 'Cancelled')\
     .group_by(Product.product_id, Product.product_sku, Product.product_name, Category.category_name, Product.unit_cost, Product.unit_price)\
     .all()

    if not query:
        return {'products': [], 'best_selling': [], 'worst_selling': [], 'matrix': {}}

    products_data = []
    total_rev_all = sum([float(r[7] or 0) for r in query]) or 1.0
    total_profit_all = sum([float(r[8] or 0) for r in query]) or 1.0
    
    avg_bench_rev = total_rev_all / len(query)
    avg_bench_profit = total_profit_all / len(query)

    for r in query:
        rev = round(float(r[7] or 0), 2)
        prof = round(float(r[8] or 0), 2)
        margin = round((prof / rev) * 100, 2) if rev > 0 else 0.0
        units = int(r[6] or 0)
        lines = int(r[10] or 1)
        returned = int(r[11] or 0)
        return_rate = round((returned / lines) * 100, 2)
        avg_disc = round(float(r[9] or 0), 2)

        # Quadrant Assignment
        if rev >= avg_bench_rev and prof >= avg_bench_profit:
            quadrant = 'Star Performers (High Rev, High Profit)'
            recommendation = 'Maintain premium positioning, maximize stock availability and bundle with emerging SKUs.'
        elif rev >= avg_bench_rev and prof < avg_bench_profit:
            quadrant = 'Volume Drivers (High Rev, Low Profit)'
            recommendation = 'High sales volume but margin dilutive. Reduce discount allowances and renegotiate supply costs.'
        elif rev < avg_bench_rev and prof >= avg_bench_profit:
            quadrant = 'Niche High Margin (Low Rev, High Profit)'
            recommendation = 'High profitability per unit. Accelerate targeted marketing and feature in executive proposals.'
        else:
            quadrant = 'Underperformers (Low Rev, Low Profit)'
            recommendation = 'Low demand and weak margin. Review product-market fit or prepare for end-of-life sunsetting.'

        products_data.append({
            'product_id': r[0],
            'sku': r[1],
            'name': r[2],
            'category': r[3],
            'unit_cost': float(r[4] or 0),
            'unit_price': float(r[5] or 0),
            'units_sold': units,
            'total_revenue': rev,
            'total_profit': prof,
            'margin_pct': margin,
            'avg_discount_pct': avg_disc,
            'return_rate_pct': return_rate,
            'quadrant': quadrant,
            'recommendation': recommendation
        })

    # Sortings for leaders and laggards
    by_units = sorted(products_data, key=lambda x: x['units_sold'], reverse=True)
    by_rev = sorted(products_data, key=lambda x: x['total_revenue'], reverse=True)
    by_profit = sorted(products_data, key=lambda x: x['total_profit'], reverse=True)
    by_margin = sorted(products_data, key=lambda x: x['margin_pct'], reverse=True)

    quadrant_counts = {
        'Star Performers': len([p for p in products_data if 'Star' in p['quadrant']]),
        'Volume Drivers': len([p for p in products_data if 'Volume' in p['quadrant']]),
        'Niche High Margin': len([p for p in products_data if 'Niche' in p['quadrant']]),
        'Underperformers': len([p for p in products_data if 'Under' in p['quadrant']])
    }

    return {
        'all_products': products_data,
        'benchmarks': {
            'avg_revenue': round(avg_bench_rev, 2),
            'avg_profit': round(avg_bench_profit, 2)
        },
        'quadrant_counts': quadrant_counts,
        'top_by_revenue': by_rev[:5],
        'bottom_by_revenue': by_rev[-5:],
        'top_by_units': by_units[:5],
        'bottom_by_units': by_units[-5:],
        'top_by_profit': by_profit[:5],
        'top_by_margin': by_margin[:5]
    }
