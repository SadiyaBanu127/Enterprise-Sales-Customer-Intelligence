import logging
from flask import Blueprint, render_template, request, jsonify
from services.auth_service import login_required_view, login_required_api
from services.analytics import (
    get_executive_kpis,
    get_monthly_revenue_trend,
    get_revenue_by_region,
    get_revenue_by_category,
    get_top_products,
    get_top_customers
)
from services.customer_segmentation import get_rfm_segment_distribution
from services.insights import generate_automated_business_insights
from models.region import Region
from models.product import Category

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required_view
def dashboard_view():
    """Renders the main executive dashboard interface."""
    regions = Region.query.all()
    categories = Category.query.all()
    return render_template(
        'dashboard.html',
        regions=regions,
        categories=categories,
        active_page='dashboard'
    )

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required_api
def api_dashboard_data():
    """Returns dynamic executive dashboard analytics with multi-parameter filtering."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    region_id = request.args.get('region_id')
    category_id = request.args.get('category_id')
    segment = request.args.get('segment')

    # 1. Fetch Executive KPIs
    kpis = get_executive_kpis(start_date, end_date, region_id, category_id, segment)

    # 2. Monthly Trends
    monthly_trend = get_monthly_revenue_trend(start_date, end_date, region_id, category_id, segment)

    # 3. Regional Breakdown
    regional_data = get_revenue_by_region(start_date, end_date, segment)

    # 4. Category Breakdown
    category_data = get_revenue_by_category(start_date, end_date, region_id, segment)

    # 5. Customer Segmentation Breakdown
    segment_data = get_rfm_segment_distribution()

    # 6. Top Products & Customers
    top_products = get_top_products(10)
    top_customers = get_top_customers(10)

    # 7. Automated Business Insights
    insights = generate_automated_business_insights()

    return jsonify({
        'success': True,
        'kpis': kpis,
        'monthly_trend': monthly_trend,
        'regional_breakdown': regional_data,
        'category_breakdown': category_data,
        'segment_distribution': segment_data,
        'top_products': top_products,
        'top_customers': top_customers,
        'insights': insights
    })
