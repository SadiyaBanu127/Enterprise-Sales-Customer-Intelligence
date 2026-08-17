import logging
from sqlalchemy import func
from database.db import db
from models.order import Order, OrderItem
from models.customer import Customer
from models.product import Product, Category
from models.region import Region

logger = logging.getLogger(__name__)

def generate_automated_business_insights():
    """Analyzes real database metrics and synthesizes dynamic, actionable business intelligence insights."""
    insights = []

    # 1. Total Revenue & Profit Margin Health Check
    kpi_q = db.session.query(
        func.sum(Order.total_amount),
        func.sum(Order.net_profit),
        func.count(Order.order_id)
    ).filter(Order.status != 'Cancelled').first()

    total_rev = float(kpi_q[0] or 0.0)
    total_profit = float(kpi_q[1] or 0.0)
    margin = round((total_profit / total_rev) * 100, 2) if total_rev > 0 else 0.0

    if margin >= 35.0:
        insights.append({
            'type': 'success',
            'category': 'Financial Performance',
            'title': 'Strong Operating Profitability',
            'summary': f'Overall profit margin stands at a robust {margin}%, reflecting high pricing power in Enterprise Software and Cybersecurity lines.',
            'action': 'Continue expanding enterprise tier software subscriptions to sustain healthy margin velocity.'
        })
    else:
        insights.append({
            'type': 'warning',
            'category': 'Financial Performance',
            'title': 'Margin Compression Alert',
            'summary': f'Overall profit margin is currently {margin}%. High hardware procurement costs and elevated discount rates are dampening net margins.',
            'action': 'Conduct cost-of-goods-sold renegotiations and set a strict 15% ceiling on sales representative discounts.'
        })

    # 2. Regional Leaders and Laggards
    reg_rev = db.session.query(
        Region.region_name,
        func.sum(Order.total_amount).label('rev'),
        func.sum(Order.net_profit).label('profit')
    ).join(Order, Region.region_id == Order.region_id)\
     .filter(Order.status != 'Cancelled')\
     .group_by(Region.region_id, Region.region_name)\
     .order_by(func.sum(Order.total_amount).desc()).all()

    if reg_rev:
        top_reg = reg_rev[0]
        bot_reg = reg_rev[-1]
        top_pct = round((float(top_reg[1]) / total_rev) * 100, 1) if total_rev > 0 else 0
        insights.append({
            'type': 'info',
            'category': 'Geographic Distribution',
            'title': f'{top_reg[0]} Leads Global Sales',
            'summary': f'{top_reg[0]} generated ${float(top_reg[1]):,.2f} ({top_pct}% of total enterprise revenue). Meanwhile, {bot_reg[0]} contributed ${float(bot_reg[1]):,.2f}.',
            'action': f'Reallocate 2 additional sales representatives from mature territories into {bot_reg[0]} to capture untapped Tier-2 enterprise demand.'
        })

    # 3. Product Profitability & Discount Leakage
    top_prod = db.session.query(
        Product.product_name,
        func.sum(OrderItem.item_total_amount).label('rev'),
        func.sum(OrderItem.item_profit).label('profit')
    ).join(OrderItem, Product.product_id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.order_id)\
     .filter(Order.status != 'Cancelled')\
     .group_by(Product.product_id, Product.product_name)\
     .order_by(func.sum(OrderItem.item_total_amount).desc()).first()

    if top_prod:
        insights.append({
            'type': 'primary',
            'category': 'Product Leadership',
            'title': f'Flagship Revenue Driver: {top_prod[0]}',
            'summary': f'Generated ${float(top_prod[1]):,.2f} with net profit contribution of ${float(top_prod[2]):,.2f}.',
            'action': 'Prioritize production capacity and feature prominently in marketing and partner co-selling programs.'
        })

    # 4. Customer Churn & Retention Risk
    total_cust = Customer.query.count() or 1
    high_churn = Customer.query.filter_by(churn_risk_level='High Risk').count()
    churn_pct = round((high_churn / total_cust) * 100, 1)

    if churn_pct > 20.0:
        insights.append({
            'type': 'danger',
            'category': 'Customer Health & Churn',
            'title': f'Elevated Churn Risk: {churn_pct}% of Accounts At Risk',
            'summary': f'{high_churn:,} accounts show prolonged inactivity (>120 days) and declining reorder frequency.',
            'action': 'Execute immediate VIP Win-Back campaigns and schedule quarterly business reviews (QBRs) for at-risk accounts.'
        })
    else:
        insights.append({
            'type': 'success',
            'category': 'Customer Health & Churn',
            'title': f'Healthy Account Retention: Only {churn_pct}% High Churn Risk',
            'summary': f'Customer engagement remains high across core segments (Champions & Loyalists).',
            'action': 'Deploy cross-sell playbooks to expand Average Order Value (AOV) across active enterprise accounts.'
        })

    return insights
