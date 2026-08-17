import os
import io
import logging
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from services.analytics import get_executive_kpis, get_revenue_by_region, get_revenue_by_category, get_top_products
from services.customer_segmentation import get_customer_kpis, get_rfm_segment_distribution
from services.churn_model import get_churn_evaluation_data, get_churn_risk_overview
from services.forecasting import get_forecast_results
from services.insights import generate_automated_business_insights

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf_report(report_type='executive_summary'):
    """Generates a high-quality multi-page PDF executive report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0369A1'),
        spaceAfter=6
    )

    elements = []

    # Title & Metadata Header
    elements.append(Paragraph("Enterprise Sales & Customer Intelligence Platform", title_style))
    report_titles = {
        'executive_summary': "Executive C-Suite Intelligence Briefing",
        'sales_performance': "Comprehensive Sales & Revenue Performance Report",
        'customer_churn': "Customer Segmentation & Churn Risk Audit",
        'sales_forecast': "Strategic Sales Forecasting & Demand Outlook"
    }
    elements.append(Paragraph(f"<b>Document:</b> {report_titles.get(report_type, 'Executive Report')} | <b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y - %H:%M UTC')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=14))

    # Pull Live Database Data
    kpis = get_executive_kpis()
    insights = generate_automated_business_insights()

    if report_type == 'executive_summary':
        elements.append(Paragraph("1. Executive Financial & Operational KPIs", h2_style))
        kpi_table_data = [
            ["Key Performance Indicator", "Current Value", "Key Performance Indicator", "Current Value"],
            ["Total Revenue", f"${kpis['total_revenue']:,.2f}", "Total Net Profit", f"${kpis['total_profit']:,.2f}"],
            ["Profit Margin", f"{kpis['profit_margin']}%", "Average Order Value (AOV)", f"${kpis['average_order_value']:,.2f}"],
            ["Total Orders Placed", f"{kpis['total_orders']:,}", "Active Customer Base", f"{kpis['total_customers']:,}"],
            ["Customer Retention Rate", f"{kpis['retention_rate']}%", "High Churn Risk Rate", f"{kpis['churn_rate']}%"]
        ]
        t = Table(kpi_table_data, colWidths=[140, 120, 140, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 14))

        # Top Regional & Category Contributions
        elements.append(Paragraph("2. Strategic Business Intelligence Insights", h2_style))
        for ins in insights:
            elements.append(Paragraph(f"<b>• [{ins['category']}] {ins['title']}</b>", body_style))
            elements.append(Paragraph(f"{ins['summary']}", body_style))
            elements.append(Paragraph(f"<i>Prescriptive Action: {ins['action']}</i>", callout_style))
            elements.append(Spacer(1, 4))

        elements.append(Spacer(1, 10))
        elements.append(Paragraph("3. Top 5 Flagship Enterprise Products", h2_style))
        top_prods = get_top_products(5)
        prod_table_data = [["Product Name", "Category", "Revenue", "Profit", "Margin %"]]
        for p in top_prods:
            prod_table_data.append([
                p['product_name'][:30],
                p['category_name'],
                f"${p['revenue']:,.2f}",
                f"${p['profit']:,.2f}",
                f"{p['margin_pct']}%"
            ])
        pt = Table(prod_table_data, colWidths=[160, 140, 75, 75, 70])
        pt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ]))
        elements.append(pt)

    elif report_type == 'sales_performance':
        elements.append(Paragraph("1. Regional Sales Breakdown", h2_style))
        reg_data = get_revenue_by_region()
        reg_table = [["Region Name", "Total Revenue", "Total Profit", "Order Count"]]
        for i in range(len(reg_data['labels'])):
            reg_table.append([
                reg_data['labels'][i],
                f"${reg_data['revenues'][i]:,.2f}",
                f"${reg_data['profits'][i]:,.2f}",
                f"{reg_data['orders'][i]:,}"
            ])
        rt = Table(reg_table, colWidths=[180, 120, 120, 100])
        rt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(rt)
        elements.append(Spacer(1, 14))

        elements.append(Paragraph("2. Product Category Distribution", h2_style))
        cat_data = get_revenue_by_category()
        cat_table = [["Category Name", "Total Revenue", "Total Profit", "Units Sold"]]
        for i in range(len(cat_data['labels'])):
            cat_table.append([
                cat_data['labels'][i],
                f"${cat_data['revenues'][i]:,.2f}",
                f"${cat_data['profits'][i]:,.2f}",
                f"{cat_data['units'][i]:,}"
            ])
        ct = Table(cat_table, colWidths=[180, 120, 120, 100])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(ct)

    elif report_type == 'customer_churn':
        elements.append(Paragraph("1. RFM Customer Segmentation Summary", h2_style))
        rfm_data = get_rfm_segment_distribution()
        rfm_table = [["Segment", "Customer Count", "% Share", "Total Revenue", "Avg Spend", "Avg Recency"]]
        for s in rfm_data['segments']:
            rfm_table.append([
                s['segment'],
                f"{s['count']:,}",
                f"{s['percentage']}%",
                f"${s['total_revenue']:,.2f}",
                f"${s['avg_spend']:,.2f}",
                f"{s['avg_recency']} days"
            ])
        rfm_t = Table(rfm_table, colWidths=[120, 80, 60, 100, 80, 80])
        rfm_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(rfm_t)
        elements.append(Spacer(1, 14))

        elements.append(Paragraph("2. Machine Learning Churn Model Performance", h2_style))
        churn_metrics = get_churn_evaluation_data()
        ml_table = [
            ["Metric", "Score", "Metric", "Score"],
            ["Algorithm", churn_metrics.get('model_name', 'Random Forest'), "ROC-AUC Score", str(churn_metrics.get('roc_auc', 'N/A'))],
            ["Classification Accuracy", f"{churn_metrics.get('accuracy', 0)*100:.1f}%", "F1 Score", str(churn_metrics.get('f1_score', 'N/A'))],
            ["Precision", f"{churn_metrics.get('precision', 0)*100:.1f}%", "Recall", f"{churn_metrics.get('recall', 0)*100:.1f}%"]
        ]
        ml_t = Table(ml_table, colWidths=[140, 120, 140, 120])
        ml_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(ml_t)

    elif report_type == 'sales_forecast':
        elements.append(Paragraph("1. Time-Series Sales Forecast & Demand Outlook", h2_style))
        fc = get_forecast_results(horizon_days=90)
        elements.append(Paragraph(f"<b>Forecasting Model:</b> {fc.get('model_name', 'Holt-Winters Exponential Smoothing')}", body_style))
        elements.append(Paragraph(f"<b>Expected Total Revenue (Next 90 Days):</b> ${fc.get('expected_revenue', 0):,.2f}", body_style))
        elements.append(Paragraph(f"<b>Projected Growth Rate:</b> {fc.get('expected_growth_rate', 0):+.2f}% vs prior period", body_style))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>Strategic Recommendation:</b> {fc.get('interpretation', '')}", callout_style))

    # Build Document
    doc.build(elements)
    buffer.seek(0)
    return buffer
