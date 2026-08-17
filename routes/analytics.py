import logging
from flask import Blueprint, render_template, request, jsonify
from services.auth_service import login_required_view, login_required_api
from services.analytics import (
    get_monthly_revenue_trend,
    get_revenue_by_region,
    get_revenue_by_category,
    get_sales_rep_performance,
    get_top_products
)
from services.customer_segmentation import (
    get_customer_kpis,
    get_rfm_segment_distribution,
    perform_kmeans_clustering,
    get_paginated_customers
)
from services.product_analytics import get_product_analytics_summary
from services.regional_analytics import get_regional_intelligence
from models.region import Region
from models.product import Category

logger = logging.getLogger(__name__)
analytics_bp = Blueprint('analytics', __name__)

# --- VIEW ROUTES ---

@analytics_bp.route('/sales')
@login_required_view
def sales_view():
    """Renders the Sales Analytics view."""
    regions = Region.query.all()
    categories = Category.query.all()
    return render_template('sales.html', regions=regions, categories=categories, active_page='sales')

@analytics_bp.route('/customers')
@login_required_view
def customers_view():
    """Renders the Customer Analytics & RFM Segmentation view."""
    regions = Region.query.all()
    return render_template('customers.html', regions=regions, active_page='customers')

@analytics_bp.route('/products')
@login_required_view
def products_view():
    """Renders the Product Analytics & Profitability Matrix view."""
    return render_template('products.html', active_page='products')

@analytics_bp.route('/regions')
@login_required_view
def regions_view():
    """Renders the Regional Analytics view."""
    return render_template('regions.html', active_page='regions')

# --- REST API ENDPOINTS ---

@analytics_bp.route('/api/sales', methods=['GET'])
@login_required_api
def api_sales():
    """Returns detailed sales trends, breakdown, and rep performance."""
    monthly_trend = get_monthly_revenue_trend()
    revenue_by_region = get_revenue_by_region()
    revenue_by_category = get_revenue_by_category()
    sales_reps = get_sales_rep_performance()
    top_products = get_top_products(10)

    return jsonify({
        'success': True,
        'monthly_trend': monthly_trend,
        'revenue_by_region': revenue_by_region,
        'revenue_by_category': revenue_by_category,
        'sales_reps': sales_reps,
        'top_products': top_products
    })

@analytics_bp.route('/api/customers', methods=['GET'])
@login_required_api
def api_customers():
    """Returns paginated customer list and high-level customer KPIs."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '').strip()
    segment = request.args.get('segment', 'all')
    risk_level = request.args.get('risk_level', 'all')
    region_id = request.args.get('region_id', 'all')

    kpis = get_customer_kpis()
    paginated_data = get_paginated_customers(page, per_page, search, segment, risk_level, region_id)

    return jsonify({
        'success': True,
        'kpis': kpis,
        'data': paginated_data
    })

@analytics_bp.route('/api/segments', methods=['GET'])
@login_required_api
def api_segments():
    """Returns RFM distribution and K-Means behavioral clusters."""
    rfm_data = get_rfm_segment_distribution()
    kmeans_data = perform_kmeans_clustering(n_clusters=4)

    return jsonify({
        'success': True,
        'rfm': rfm_data,
        'kmeans': kmeans_data
    })

@analytics_bp.route('/api/products', methods=['GET'])
@login_required_api
def api_products():
    """Returns product profitability 4-quadrant scatter matrix and SKU performance."""
    data = get_product_analytics_summary()
    return jsonify({
        'success': True,
        'data': data
    })

@analytics_bp.route('/api/regions', methods=['GET'])
@login_required_api
def api_regions():
    """Returns regional intelligence and market standouts."""
    data = get_regional_intelligence()
    return jsonify({
        'success': True,
        'data': data
    })
