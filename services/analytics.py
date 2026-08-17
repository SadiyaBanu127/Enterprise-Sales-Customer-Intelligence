import logging
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import func, case
from database.db import db
from models.order import Order, OrderItem
from models.customer import Customer
from models.product import Product, Category
from models.region import Region, SalesRep

logger = logging.getLogger(__name__)

def build_order_filter_query(start_date=None, end_date=None, region_id=None, category_id=None, segment=None):
    """Builds a filtered base SQLAlchemy query for orders joined with customers, products and categories."""
    query = db.session.query(Order).join(Customer, Order.customer_id == Customer.customer_id)
    
    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)
    if region_id and region_id not in ('all', '', None):
        query = query.filter(Order.region_id == int(region_id))
    if segment and segment not in ('all', '', None):
        query = query.filter(Customer.segment == segment)
    if category_id and category_id not in ('all', '', None):
        query = query.join(OrderItem, Order.order_id == OrderItem.order_id)\
                     .join(Product, OrderItem.product_id == Product.product_id)\
                     .filter(Product.category_id == int(category_id))

    return query

def get_executive_kpis(start_date=None, end_date=None, region_id=None, category_id=None, segment=None):
    """Calculates all executive high-level KPI cards."""
    # Base completed orders
    base_q = build_order_filter_query(start_date, end_date, region_id, category_id, segment)
    completed_q = base_q.filter(Order.status != 'Cancelled')

    total_revenue = completed_q.with_entities(func.sum(Order.total_amount)).scalar() or 0.0
    total_cost = completed_q.with_entities(func.sum(Order.total_cost)).scalar() or 0.0
    total_profit = completed_q.with_entities(func.sum(Order.net_profit)).scalar() or 0.0
    total_orders = completed_q.with_entities(func.count(Order.order_id)).scalar() or 0
    unique_customers_count = completed_q.with_entities(func.count(func.distinct(Order.customer_id))).scalar() or 0

    # Total customers in DB
    all_cust_q = db.session.query(Customer)
    if region_id and region_id not in ('all', '', None):
        all_cust_q = all_cust_q.filter(Customer.region_id == int(region_id))
    if segment and segment not in ('all', '', None):
        all_cust_q = all_cust_q.filter(Customer.segment == segment)
    total_customers = all_cust_q.count() or 1

    # Repeat Customers & Retention
    repeat_customers = all_cust_q.filter(Customer.total_orders_count > 1).count()
    retention_rate = round((repeat_customers / total_customers) * 100, 2) if total_customers > 0 else 0.0

    # Churn Rate
    high_churn_customers = all_cust_q.filter(Customer.churn_risk_level == 'High Risk').count()
    churn_rate = round((high_churn_customers / total_customers) * 100, 2) if total_customers > 0 else 0.0

    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
    profit_margin = round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0.0

    return {
        'total_revenue': float(total_revenue),
        'total_profit': float(total_profit),
        'total_cost': float(total_cost),
        'total_orders': int(total_orders),
        'total_customers': int(total_customers),
        'active_purchasers': int(unique_customers_count),
        'average_order_value': float(avg_order_value),
        'profit_margin': float(profit_margin),
        'retention_rate': float(retention_rate),
        'churn_rate': float(churn_rate)
    }

def get_monthly_revenue_trend(start_date=None, end_date=None, region_id=None, category_id=None, segment=None):
    """Calculates monthly revenue, profit and MoM growth rate."""
    query = build_order_filter_query(start_date, end_date, region_id, category_id, segment)\
        .filter(Order.status != 'Cancelled')\
        .with_entities(
            func.strftime('%Y-%m', Order.order_date).label('month'),
            func.sum(Order.total_amount).label('revenue'),
            func.sum(Order.net_profit).label('profit'),
            func.count(Order.order_id).label('orders_count')
        )\
        .group_by('month')\
        .order_by('month')

    results = query.all()
    
    months = []
    revenues = []
    profits = []
    orders = []
    growth_rates = []

    prev_rev = None
    for r in results:
        m, rev, prof, ord_c = r[0], float(r[1] or 0), float(r[2] or 0), int(r[3] or 0)
        months.append(m)
        revenues.append(round(rev, 2))
        profits.append(round(prof, 2))
        orders.append(ord_c)
        
        if prev_rev and prev_rev > 0:
            growth = round(((rev - prev_rev) / prev_rev) * 100, 2)
        else:
            growth = 0.0
        growth_rates.append(growth)
        prev_rev = rev

    return {
        'labels': months,
        'revenues': revenues,
        'profits': profits,
        'orders': orders,
        'growth_rates': growth_rates
    }

def get_revenue_by_region(start_date=None, end_date=None, segment=None):
    """Calculates revenue and profit breakdown by geographic region."""
    query = db.session.query(
        Region.region_name,
        func.sum(Order.total_amount).label('revenue'),
        func.sum(Order.net_profit).label('profit'),
        func.count(Order.order_id).label('order_count')
    ).join(Order, Region.region_id == Order.region_id)\
     .join(Customer, Order.customer_id == Customer.customer_id)\
     .filter(Order.status != 'Cancelled')

    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)
    if segment and segment not in ('all', '', None):
        query = query.filter(Customer.segment == segment)

    query = query.group_by(Region.region_id, Region.region_name).order_by(func.sum(Order.total_amount).desc())
    results = query.all()

    labels = [r[0] for r in results]
    revenues = [round(float(r[1] or 0), 2) for r in results]
    profits = [round(float(r[2] or 0), 2) for r in results]
    orders = [int(r[3] or 0) for r in results]

    return {
        'labels': labels,
        'revenues': revenues,
        'profits': profits,
        'orders': orders
    }

def get_revenue_by_category(start_date=None, end_date=None, region_id=None, segment=None):
    """Calculates sales and profit breakdown across product categories."""
    query = db.session.query(
        Category.category_name,
        func.sum(OrderItem.item_total_amount).label('revenue'),
        func.sum(OrderItem.item_profit).label('profit'),
        func.sum(OrderItem.quantity).label('units_sold')
    ).join(Product, Category.category_id == Product.category_id)\
     .join(OrderItem, Product.product_id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.order_id)\
     .join(Customer, Order.customer_id == Customer.customer_id)\
     .filter(Order.status != 'Cancelled')

    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)
    if region_id and region_id not in ('all', '', None):
        query = query.filter(Order.region_id == int(region_id))
    if segment and segment not in ('all', '', None):
        query = query.filter(Customer.segment == segment)

    query = query.group_by(Category.category_id, Category.category_name).order_by(func.sum(OrderItem.item_total_amount).desc())
    results = query.all()

    labels = [r[0] for r in results]
    revenues = [round(float(r[1] or 0), 2) for r in results]
    profits = [round(float(r[2] or 0), 2) for r in results]
    units = [int(r[3] or 0) for r in results]

    return {
        'labels': labels,
        'revenues': revenues,
        'profits': profits,
        'units': units
    }

def get_top_products(limit=10):
    """Retrieves top products ranked by revenue and profit."""
    query = db.session.query(
        Product.product_name,
        Category.category_name,
        func.sum(OrderItem.item_total_amount).label('revenue'),
        func.sum(OrderItem.item_profit).label('profit'),
        func.sum(OrderItem.quantity).label('units_sold')
    ).join(Category, Product.category_id == Category.category_id)\
     .join(OrderItem, Product.product_id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.order_id)\
     .filter(Order.status != 'Cancelled')\
     .group_by(Product.product_id, Product.product_name, Category.category_name)\
     .order_by(func.sum(OrderItem.item_total_amount).desc())\
     .limit(limit)

    results = query.all()
    return [{
        'product_name': r[0],
        'category_name': r[1],
        'revenue': round(float(r[2] or 0), 2),
        'profit': round(float(r[3] or 0), 2),
        'units_sold': int(r[4] or 0),
        'margin_pct': round((float(r[3] or 0) / float(r[2] or 1)) * 100, 2) if r[2] else 0.0
    } for r in results]

def get_top_customers(limit=10):
    """Retrieves top 10 customers by revenue and orders count."""
    query = db.session.query(
        Customer.customer_code,
        Customer.customer_name,
        Customer.company_name,
        Customer.segment,
        Region.region_name,
        Customer.total_orders_count,
        Customer.total_spend,
        Customer.average_order_value,
        Customer.churn_risk_level
    ).join(Region, Customer.region_id == Region.region_id)\
     .order_by(Customer.total_spend.desc())\
     .limit(limit)

    results = query.all()
    return [{
        'customer_code': r[0],
        'customer_name': r[1],
        'company_name': r[2] or 'Individual',
        'segment': r[3],
        'region_name': r[4],
        'total_orders': int(r[5] or 0),
        'total_spend': round(float(r[6] or 0), 2),
        'average_order_value': round(float(r[7] or 0), 2),
        'churn_risk_level': r[8]
    } for r in results]

def get_sales_rep_performance():
    """Retrieves Sales Representative leaderboard and quota attainment."""
    query = db.session.query(
        SalesRep.rep_code,
        SalesRep.rep_name,
        Region.region_name,
        SalesRep.quota_annual,
        func.sum(Order.total_amount).label('revenue_generated'),
        func.sum(Order.net_profit).label('profit_generated'),
        func.count(Order.order_id).label('deals_closed')
    ).join(Region, SalesRep.region_id == Region.region_id)\
     .outerjoin(Order, SalesRep.rep_id == Order.rep_id)\
     .filter(Order.status != 'Cancelled')\
     .group_by(SalesRep.rep_id, SalesRep.rep_code, SalesRep.rep_name, Region.region_name, SalesRep.quota_annual)\
     .order_by(func.sum(Order.total_amount).desc())

    results = query.all()
    reps_data = []
    for r in results:
        quota = float(r[3] or 500000.0)
        rev = float(r[4] or 0.0)
        attainment = round((rev / quota) * 100, 2) if quota > 0 else 0.0
        reps_data.append({
            'rep_code': r[0],
            'rep_name': r[1],
            'region_name': r[2],
            'quota': quota,
            'revenue': round(rev, 2),
            'profit': round(float(r[5] or 0.0), 2),
            'deals_closed': int(r[6] or 0),
            'attainment_pct': attainment,
            'status': 'Quota Exceeded' if attainment >= 100 else ('On Track' if attainment >= 80 else 'Underperforming')
        })
    return reps_data
