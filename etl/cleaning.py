import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DataCleaner:
    """Production-grade Data Cleaning and Validation Module."""

    def __init__(self):
        self.audit_log = {}

    def clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates customer records."""
        initial_count = len(df)
        
        # 1. Deduplication
        df = df.drop_duplicates(subset=['customer_code']).copy()
        
        # 2. Handle missing values
        df['company_name'] = df['company_name'].fillna('Individual Account')
        df['email'] = df['email'].fillna('no-email@domain.com')
        df['segment'] = df['segment'].fillna('Standard')
        
        # 3. Clean date format strictly as YYYY-MM-DD
        df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
        df['signup_date'] = df['signup_date'].fillna(pd.Timestamp('2023-01-01')).dt.strftime('%Y-%m-%d')
        
        # 4. Type conversions
        df['region_id'] = pd.to_numeric(df['region_id'], errors='coerce').fillna(1).astype(int)
        df['is_active'] = df['is_active'].fillna(True).astype(bool)

        self.audit_log['customers'] = {
            'initial_rows': initial_count,
            'cleaned_rows': len(df),
            'duplicates_removed': initial_count - len(df),
            'null_values_handled': int(df.isnull().sum().sum())
        }
        return df

    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates product catalog records."""
        initial_count = len(df)
        df = df.drop_duplicates(subset=['product_sku']).copy()

        # Numeric validations
        df['unit_cost'] = pd.to_numeric(df['unit_cost'], errors='coerce').fillna(0.0)
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0.0)
        
        # Outlier handling / Negative value protection
        df['unit_cost'] = df['unit_cost'].apply(lambda x: max(1.0, float(x)))
        df['unit_price'] = df['unit_price'].apply(lambda x: max(2.0, float(x)))
        
        # Calculate target margin
        df['target_margin_pct'] = np.where(
            df['unit_price'] > 0,
            np.round(((df['unit_price'] - df['unit_cost']) / df['unit_price']) * 100, 2),
            0.0
        )
        df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce').fillna(50).astype(int)
        df['is_discontinued'] = df['is_discontinued'].fillna(False).astype(bool)

        self.audit_log['products'] = {
            'initial_rows': initial_count,
            'cleaned_rows': len(df),
            'duplicates_removed': initial_count - len(df)
        }
        return df

    def clean_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates order transactions."""
        initial_count = len(df)
        df = df.drop_duplicates(subset=['order_number']).copy()

        # Date parsing strictly as YYYY-MM-DD
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df['order_date'] = df['order_date'].fillna(pd.Timestamp('2024-01-01')).dt.strftime('%Y-%m-%d')

        # Clean numeric financial columns safely
        num_cols = ['subtotal_amount', 'discount_amount', 'shipping_cost', 'total_amount', 'total_cost', 'net_profit']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            else:
                df[col] = 0.0

        # Sanity check total_amount
        df['total_amount'] = np.where(
            df['total_amount'] < 0,
            np.abs(df['total_amount']),
            df['total_amount']
        )
        
        # Re-derive margin pct safely
        df['profit_margin_pct'] = np.where(
            df['total_amount'] > 0,
            np.round((df['net_profit'] / df['total_amount']) * 100, 2),
            0.0
        )

        df['status'] = df['status'].fillna('Completed')
        df['is_returned'] = df['is_returned'].fillna(False).astype(bool)

        self.audit_log['orders'] = {
            'initial_rows': initial_count,
            'cleaned_rows': len(df),
            'duplicates_removed': initial_count - len(df)
        }
        return df

    def clean_order_items(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans order items and line metrics."""
        initial_count = len(df)
        df = df.drop_duplicates(subset=['item_id']).copy()

        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
        df['quantity'] = df['quantity'].apply(lambda q: max(1, min(q, 500))) # Cap reasonable range

        df['discount_pct'] = pd.to_numeric(df['discount_pct'], errors='coerce').fillna(0.0)
        df['discount_pct'] = df['discount_pct'].apply(lambda d: max(0.0, min(float(d), 50.0)))

        df['item_total_amount'] = pd.to_numeric(df['item_total_amount'], errors='coerce').fillna(0.0)
        df['item_total_cost'] = pd.to_numeric(df['item_total_cost'], errors='coerce').fillna(0.0)
        df['item_profit'] = pd.to_numeric(df['item_profit'], errors='coerce').fillna(0.0)

        self.audit_log['order_items'] = {
            'initial_rows': initial_count,
            'cleaned_rows': len(df),
            'duplicates_removed': initial_count - len(df)
        }
        return df

    def get_audit_summary(self):
        return self.audit_log
