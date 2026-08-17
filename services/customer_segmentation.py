import logging
import pandas as pd
import numpy as np
from sqlalchemy import func
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from database.db import db
from models.customer import Customer
from models.region import Region

logger = logging.getLogger(__name__)

def get_customer_kpis():
    """Calculates overall customer analytics high-level KPIs."""
    total_customers = Customer.query.count() or 1
    new_customers = Customer.query.filter(Customer.segment == 'New Customers').count()
    returning_customers = Customer.query.filter(Customer.total_orders_count > 1).count()
    repeat_rate = round((returning_customers / total_customers) * 100, 2)
    
    avg_clv = db.session.query(func.avg(Customer.total_spend)).scalar() or 0.0
    avg_recency = db.session.query(func.avg(Customer.recency_days)).scalar() or 0.0
    avg_orders = db.session.query(func.avg(Customer.total_orders_count)).scalar() or 0.0

    return {
        'total_customers': total_customers,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'repeat_purchase_rate': repeat_rate,
        'average_customer_clv': round(float(avg_clv), 2),
        'average_recency_days': round(float(avg_recency), 1),
        'average_orders_per_customer': round(float(avg_orders), 1)
    }

def get_rfm_segment_distribution():
    """Returns customer distribution and average metrics across all RFM segments."""
    segments_query = db.session.query(
        Customer.segment,
        func.count(Customer.customer_id).label('customer_count'),
        func.sum(Customer.total_spend).label('total_revenue'),
        func.avg(Customer.total_spend).label('avg_spend'),
        func.avg(Customer.recency_days).label('avg_recency'),
        func.avg(Customer.total_orders_count).label('avg_frequency')
    ).group_by(Customer.segment).order_by(func.sum(Customer.total_spend).desc()).all()

    total_customers = sum([r[1] for r in segments_query]) or 1

    segments_data = []
    for r in segments_query:
        seg_name = r[0] or 'Standard'
        count = int(r[1])
        pct = round((count / total_customers) * 100, 2)
        tot_rev = round(float(r[2] or 0), 2)
        avg_sp = round(float(r[3] or 0), 2)
        avg_rec = round(float(r[4] or 0), 1)
        avg_freq = round(float(r[5] or 0), 1)

        segments_data.append({
            'segment': seg_name,
            'count': count,
            'percentage': pct,
            'total_revenue': tot_rev,
            'avg_spend': avg_sp,
            'avg_recency': avg_rec,
            'avg_frequency': avg_freq
        })

    # Prepare chart formatted structures
    labels = [s['segment'] for s in segments_data]
    counts = [s['count'] for s in segments_data]
    revenues = [s['total_revenue'] for s in segments_data]

    return {
        'segments': segments_data,
        'chart_labels': labels,
        'chart_counts': counts,
        'chart_revenues': revenues
    }

def perform_kmeans_clustering(n_clusters=4):
    """Performs K-Means clustering on customer RFM features."""
    customers = Customer.query.filter(Customer.total_orders_count > 0).limit(5000).all()
    if not customers or len(customers) < n_clusters:
        return {'clusters': [], 'cluster_centers': []}

    data = []
    for c in customers:
        data.append([
            c.recency_days or 0,
            c.total_orders_count or 1,
            float(c.total_spend or 0.0)
        ])

    X = np.array(data)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Inverse transform cluster centers to original scale
    centers = scaler.inverse_transform(kmeans.cluster_centers_)

    cluster_summaries = []
    for i in range(n_clusters):
        c_count = int(np.sum(labels == i))
        cluster_summaries.append({
            'cluster_id': i + 1,
            'name': f"Behavioral Cluster {i + 1}",
            'customer_count': c_count,
            'percentage': round((c_count / len(X)) * 100, 2),
            'avg_recency_days': round(float(centers[i][0]), 1),
            'avg_frequency_orders': round(float(centers[i][1]), 1),
            'avg_monetary_spend': round(float(centers[i][2]), 2)
        })

    return {
        'clusters': cluster_summaries
    }

def get_paginated_customers(page=1, per_page=20, search='', segment='all', risk_level='all', region_id='all'):
    """Retrieves filtered, searchable, and paginated customer list."""
    query = db.session.query(Customer).join(Region, Customer.region_id == Region.region_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.customer_name.ilike(search_pattern)) |
            (Customer.customer_code.ilike(search_pattern)) |
            (Customer.company_name.ilike(search_pattern)) |
            (Customer.email.ilike(search_pattern))
        )

    if segment and segment != 'all':
        query = query.filter(Customer.segment == segment)

    if risk_level and risk_level != 'all':
        query = query.filter(Customer.churn_risk_level == risk_level)

    if region_id and region_id != 'all':
        query = query.filter(Customer.region_id == int(region_id))

    total = query.count()
    items = query.order_by(Customer.total_spend.desc())\
                 .offset((page - 1) * per_page)\
                 .limit(per_page)\
                 .all()

    return {
        'items': [c.to_dict() for c in items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }
