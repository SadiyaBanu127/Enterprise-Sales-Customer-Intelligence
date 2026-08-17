import logging
from flask import Blueprint, render_template, request, send_file, jsonify, flash
from services.auth_service import login_required_view, login_required_api
from services.reports import create_pdf_report

logger = logging.getLogger(__name__)
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required_view
def reports_view():
    """Renders the downloadable reports center."""
    return render_template('reports.html', active_page='reports')

@reports_bp.route('/api/reports/download/<string:report_type>', methods=['GET'])
@login_required_view
def download_pdf_report(report_type):
    """Generates and streams high-res PDF executive reports."""
    allowed_reports = ['executive_summary', 'sales_performance', 'customer_churn', 'sales_forecast']
    if report_type not in allowed_reports:
        report_type = 'executive_summary'

    try:
        pdf_buffer = create_pdf_report(report_type=report_type)
        filename = f"{report_type}_report.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        flash(f"Failed to generate report: {str(e)}", "danger")
        return jsonify({'success': False, 'error': str(e)}), 500
