import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask
from config import get_config
from database.db import db
from database.init_db import init_database
from etl.generate_dataset import generate_all_data
from etl.cleaning import DataCleaner
from models.customer import Customer
from models.order import Order, OrderItem
from models.product import Product, Category
from models.region import Region, SalesRep
from models.user import User

RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

def run_etl_pipeline(force_regenerate=False):
    """Executes the full Extract-Transform-Load pipeline."""
    start_time = time.time()
    print("==================================================")
    print("[*] Starting Enterprise Data Analytics ETL Pipeline")
    print("==================================================")

    # 1. Check or generate raw datasets
    customers_csv = RAW_DIR / 'customers.csv'
    orders_csv = RAW_DIR / 'orders.csv'
    
    if force_regenerate or not customers_csv.exists() or not orders_csv.exists():
        from etl.generate_dataset import generate_all_data
        generate_all_data()

    # 2. Initialize Flask App & Database Context
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)

    with app.app_context():
        init_database(app)
        cleaner = DataCleaner()

        # 3. Read Raw CSVs
        print("[*] Extracting raw datasets from CSV...")
        df_regions = pd.read_csv(RAW_DIR / 'regions.csv')
        df_categories = pd.read_csv(RAW_DIR / 'categories.csv')
        df_products = pd.read_csv(RAW_DIR / 'products.csv')
        df_sales_reps = pd.read_csv(RAW_DIR / 'sales_reps.csv')
        df_customers = pd.read_csv(RAW_DIR / 'customers.csv')
        df_orders = pd.read_csv(RAW_DIR / 'orders.csv')
        df_order_items = pd.read_csv(RAW_DIR / 'order_items.csv')

        # 4. Transform & Clean
        print("[*] Transforming and cleaning data...")
        df_customers = cleaner.clean_customers(df_customers)
        df_products = cleaner.clean_products(df_products)
        df_orders = cleaner.clean_orders(df_orders)
        df_order_items = cleaner.clean_order_items(df_order_items)

        # 5. Compute Customer-Level Aggregations & RFM Scores
        print("[*] Computing Customer RFM segmentation and customer metrics...")
        reference_date = pd.to_datetime('2026-08-01')

        # Aggregate customer orders
        order_metrics = df_orders[df_orders['status'] != 'Cancelled'].groupby('customer_id').agg(
            total_orders_count=('order_id', 'count'),
            total_spend=('total_amount', 'sum'),
            average_order_value=('total_amount', 'mean'),
            last_purchase_date=('order_date', 'max')
        ).reset_index()

        order_metrics['last_purchase_date'] = pd.to_datetime(order_metrics['last_purchase_date'])
        order_metrics['recency_days'] = (reference_date - order_metrics['last_purchase_date']).dt.days.fillna(999).astype(int)

        # Merge with all customers
        cust_merged = df_customers.merge(order_metrics, on='customer_id', how='left')
        cust_merged['total_orders_count'] = cust_merged['total_orders_count'].fillna(0).astype(int)
        cust_merged['total_spend'] = cust_merged['total_spend'].fillna(0.0).round(2)
        cust_merged['average_order_value'] = cust_merged['average_order_value'].fillna(0.0).round(2)
        cust_merged['recency_days'] = cust_merged['recency_days'].fillna(999).astype(int)

        # Calculate RFM Scores (1 to 5 quintiles)
        try:
            cust_merged['recency_score'] = pd.qcut(cust_merged['recency_days'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
        except Exception:
            cust_merged['recency_score'] = 3

        try:
            cust_merged['frequency_score'] = pd.qcut(cust_merged['total_orders_count'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        except Exception:
            cust_merged['frequency_score'] = 3

        try:
            cust_merged['monetary_score'] = pd.qcut(cust_merged['total_spend'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        except Exception:
            cust_merged['monetary_score'] = 3

        cust_merged['rfm_score'] = (
            cust_merged['recency_score'] * 100 + 
            cust_merged['frequency_score'] * 10 + 
            cust_merged['monetary_score']
        )

        def assign_segment(row):
            r, f, m = row['recency_score'], row['frequency_score'], row['monetary_score']
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'Potential Loyalists'
            elif r >= 4 and f == 1:
                return 'New Customers'
            elif r <= 2 and f >= 3:
                return 'At Risk'
            else:
                return 'Lost Customers'

        cust_merged['segment'] = cust_merged.apply(assign_segment, axis=1)

        cust_merged['churn_risk_score'] = np.clip(
            (cust_merged['recency_days'] / 500.0) * 0.5 + 
            (1.0 / (cust_merged['total_orders_count'] + 1)) * 0.3 + 
            np.random.normal(0, 0.05, len(cust_merged)),
            0.01, 0.99
        ).round(4)

        cust_merged['churn_risk_level'] = np.where(
            cust_merged['churn_risk_score'] >= 0.70, 'High Risk',
            np.where(cust_merged['churn_risk_score'] >= 0.40, 'Medium Risk', 'Low Risk')
        )
        
        cust_merged['last_purchase_date'] = cust_merged['last_purchase_date'].dt.strftime('%Y-%m-%d')

        # 6. Load into Database via Engine
        engine = db.engine
        print(f"[*] Loading cleaned tables into Database: {engine.url.render_as_string(hide_password=True)}...")

        with engine.connect() as conn:
            conn.execute(db.text("DELETE FROM order_items"))
            conn.execute(db.text("DELETE FROM orders"))
            conn.execute(db.text("DELETE FROM customers"))
            conn.execute(db.text("DELETE FROM sales_reps"))
            conn.execute(db.text("DELETE FROM products"))
            conn.execute(db.text("DELETE FROM categories"))
            conn.execute(db.text("DELETE FROM regions"))
            conn.commit()

        # Load Reference Tables
        df_regions.to_sql('regions', con=engine, if_exists='append', index=False)
        df_categories.to_sql('categories', con=engine, if_exists='append', index=False)
        df_products.to_sql('products', con=engine, if_exists='append', index=False)
        df_sales_reps.to_sql('sales_reps', con=engine, if_exists='append', index=False)
        
        # Load fully enriched customers
        print(f"[*] Inserting {len(cust_merged):,} enriched customers...")
        cust_merged.to_sql('customers', con=engine, if_exists='append', index=False, chunksize=3000)

        # Load Orders
        print(f"[*] Inserting {len(df_orders):,} orders...")
        df_orders.to_sql('orders', con=engine, if_exists='append', index=False, chunksize=3000)

        # Load Order Items
        print(f"[*] Inserting {len(df_order_items):,} order items...")
        df_order_items.to_sql('order_items', con=engine, if_exists='append', index=False, chunksize=5000)

        # 7. Export Power BI-Ready Denormalized Flat CSV
        print("[*] Generating Power BI-Ready analytical dataset...")
        powerbi_df = df_order_items.merge(df_orders, on='order_id', suffixes=('', '_order'))
        powerbi_df = powerbi_df.merge(df_products, on='product_id', suffixes=('', '_prod'))
        powerbi_df = powerbi_df.merge(df_categories, on='category_id', suffixes=('', '_cat'))
        powerbi_df = powerbi_df.merge(cust_merged[['customer_id', 'customer_code', 'customer_name', 'segment', 'rfm_score', 'churn_risk_level']], on='customer_id')
        powerbi_df = powerbi_df.merge(df_regions, on='region_id')
        powerbi_df = powerbi_df.merge(df_sales_reps[['rep_id', 'rep_name']], on='rep_id', how='left')

        powerbi_output_path = PROCESSED_DIR / 'powerbi_sales_intelligence.csv'
        powerbi_df.to_csv(powerbi_output_path, index=False)
        print(f"[+] Saved Power BI dataset ({len(powerbi_df):,} rows) to: {powerbi_output_path}")

        elapsed = round(time.time() - start_time, 2)
        print("==================================================")
        print(f"[+] ETL Pipeline Completed in {elapsed} seconds!")
        print(f"   - Total Customers:   {len(df_customers):,}")
        print(f"   - Total Orders:      {len(df_orders):,}")
        print(f"   - Total Order Items: {len(df_order_items):,}")
        print("==================================================")

        return cleaner.get_audit_summary()

if __name__ == '__main__':
    run_etl_pipeline(force_regenerate=True)
