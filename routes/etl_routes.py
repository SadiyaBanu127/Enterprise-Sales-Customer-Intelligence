import os
import io
import logging
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
from werkzeug.utils import secure_filename
from services.auth_service import login_required_view, admin_required_view, login_required_api, admin_required_api
from etl.cleaning import DataCleaner
from etl.pipeline import run_etl_pipeline
from database.db import db
from models.order import Order

logger = logging.getLogger(__name__)
etl_bp = Blueprint('etl', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@etl_bp.route('/data-upload')
@login_required_view
def upload_view():
    """Renders the CSV dataset upload and ETL pipeline manager view."""
    return render_template('upload.html', active_page='upload')

@etl_bp.route('/api/upload', methods=['POST'])
@login_required_api
@admin_required_api
def api_upload_file():
    """Handles CSV/Excel dataset upload, data validation, and initiates cleaning pipeline."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded in request'}), 400

    file = request.files['file']
    dataset_type = request.form.get('dataset_type', 'orders')

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload a valid CSV or Excel file.'}), 400

    filename = secure_filename(file.filename)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # File validation metrics
        total_rows = len(df)
        total_cols = len(df.columns)
        null_counts = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        # Clean using DataCleaner
        cleaner = DataCleaner()
        if dataset_type == 'orders':
            cleaned_df = cleaner.clean_orders(df)
        elif dataset_type == 'customers':
            cleaned_df = cleaner.clean_customers(df)
        elif dataset_type == 'products':
            cleaned_df = cleaner.clean_products(df)
        else:
            cleaned_df = df.copy()

        # Preview first 5 rows
        preview = cleaned_df.head(5).to_dict(orient='records')

        return jsonify({
            'success': True,
            'filename': filename,
            'dataset_type': dataset_type,
            'summary': {
                'total_rows_received': total_rows,
                'total_columns': total_cols,
                'null_values_detected': null_counts,
                'duplicates_detected': duplicate_rows,
                'cleaned_rows_ready': len(cleaned_df)
            },
            'columns': list(cleaned_df.columns),
            'preview': preview
        })

    except Exception as e:
        logger.error(f"Error processing uploaded dataset: {e}")
        return jsonify({'success': False, 'error': f'Failed to process file: {str(e)}'}), 500

@etl_bp.route('/api/etl/trigger', methods=['POST'])
@login_required_api
@admin_required_api
def api_trigger_etl():
    """Triggers the full ETL pipeline execution asynchronously/synchronously."""
    try:
        audit = run_etl_pipeline(force_regenerate=False)
        return jsonify({
            'success': True,
            'message': 'ETL Pipeline executed successfully.',
            'audit_summary': audit
        })
    except Exception as e:
        logger.error(f"ETL execution failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
