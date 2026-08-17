import pandas as pd
from etl.cleaning import DataCleaner

def test_cleaner_customers():
    cleaner = DataCleaner()
    raw_data = pd.DataFrame([
        {'customer_code': 'C-1', 'customer_name': 'Alice', 'email': None, 'company_name': None, 'region_id': '1', 'signup_date': '2023-05-10', 'segment': None, 'is_active': 1},
        {'customer_code': 'C-1', 'customer_name': 'Alice Duplicate', 'email': 'alice@test.com', 'company_name': 'Acme', 'region_id': '1', 'signup_date': '2023-05-10', 'segment': 'Standard', 'is_active': 1}
    ])
    cleaned = cleaner.clean_customers(raw_data)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]['company_name'] == 'Individual Account'

def test_cleaner_orders():
    cleaner = DataCleaner()
    raw_orders = pd.DataFrame([
        {'order_number': 'ORD-001', 'order_date': '2024-01-15', 'total_amount': -150.0, 'net_profit': -50.0, 'status': None, 'is_returned': None}
    ])
    cleaned = cleaner.clean_orders(raw_orders)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]['total_amount'] == 150.0
    assert cleaned.iloc[0]['status'] == 'Completed'
