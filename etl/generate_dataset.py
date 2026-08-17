import os
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from faker import Faker

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configuration Constants
NUM_CUSTOMERS = 10500      # 10,000+ customers requirement
NUM_ORDERS = 32000         # 30,000+ orders requirement
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 7, 31)

REGIONS_DATA = [
    {'region_id': 1, 'region_name': 'North America - East', 'country': 'United States', 'market_tier': 'Tier 1', 'target_growth_rate': 14.50},
    {'region_id': 2, 'region_name': 'North America - West', 'country': 'United States', 'market_tier': 'Tier 1', 'target_growth_rate': 18.00},
    {'region_id': 3, 'region_name': 'North America - Central', 'country': 'United States', 'market_tier': 'Tier 2', 'target_growth_rate': 11.00},
    {'region_id': 4, 'region_name': 'North America - South', 'country': 'United States', 'market_tier': 'Tier 2', 'target_growth_rate': 15.20}
]

CATEGORIES_DATA = [
    {'category_id': 1, 'category_name': 'Enterprise Cloud Software', 'description': 'SaaS subscriptions, enterprise licenses, AI developer seats', 'target_margin': 78.50},
    {'category_id': 2, 'category_name': 'Hardware & Servers', 'description': 'Rackmount servers, edge compute units, high-performance switches', 'target_margin': 32.00},
    {'category_id': 3, 'category_name': 'Professional Services', 'description': 'Implementation consulting, data migration, security audits', 'target_margin': 55.00},
    {'category_id': 4, 'category_name': 'Cybersecurity Solutions', 'description': 'Endpoint protection, SIEM infrastructure, zero-trust gateways', 'target_margin': 68.00},
    {'category_id': 5, 'category_name': 'Data & AI Infrastructure', 'description': 'Vector DB appliances, GPU clusters, data lakehouse integrations', 'target_margin': 48.00}
]

PRODUCTS_SPEC = [
    # Enterprise Cloud Software
    ('ECS-101', 'CloudSphere Enterprise SaaS (Annual License)', 1, 1200.00, 3600.00, 500),
    ('ECS-102', 'OmniChannel CRM Pro Suite', 1, 450.00, 1500.00, 450),
    ('ECS-103', 'Workforce AI Automation Engine', 1, 800.00, 2400.00, 350),
    ('ECS-104', 'Cloud Analytics Developer Seat (50-Pack)', 1, 600.00, 1800.00, 400),
    ('ECS-105', 'Microservices Orchestration Platform', 1, 1500.00, 4200.00, 300),
    ('ECS-106', 'Secure Enterprise File Sync & Share', 1, 200.00, 650.00, 600),

    # Hardware & Servers
    ('HWS-201', 'HyperBlade 4U Rackmount Server', 2, 4200.00, 6500.00, 120),
    ('HWS-202', 'QuantumEdge Edge Compute Gateway', 2, 1800.00, 2900.00, 180),
    ('HWS-203', '100Gbps Enterprise Core Switch', 2, 2600.00, 3800.00, 150),
    ('HWS-204', 'OptiStore NVMe SAN Array (48TB)', 2, 6500.00, 9400.00, 80),
    ('HWS-205', 'Redundant Power Distribution Unit 30A', 2, 350.00, 580.00, 250),
    ('HWS-206', 'High-Density Server Enclosure 42U', 2, 950.00, 1450.00, 110),

    # Professional Services
    ('PRS-301', 'Enterprise Cloud Migration Package', 3, 3000.00, 7500.00, 90),
    ('PRS-302', 'SOC-2 Compliance & Security Audit', 3, 2200.00, 5200.00, 100),
    ('PRS-303', '24/7 Dedicated Technical Account Mgmt', 3, 1400.00, 3200.00, 150),
    ('PRS-304', 'Custom AI Pipeline Architecture Workshop', 3, 1800.00, 4500.00, 80),
    ('PRS-305', 'Database Performance Tuning Sprint', 3, 1100.00, 2600.00, 120),

    # Cybersecurity Solutions
    ('CYB-401', 'ZeroTrust Identity & Access Shield', 4, 900.00, 2800.00, 320),
    ('CYB-402', 'Next-Gen Firewall Appliance XG-8000', 4, 3100.00, 5600.00, 140),
    ('CYB-403', 'Automated Threat Hunting & SIEM Pro', 4, 1600.00, 4800.00, 220),
    ('CYB-404', 'Data Loss Prevention (DLP) Endpoint Guard', 4, 500.00, 1400.00, 400),
    ('CYB-405', 'Cloud Workload Protection Suite', 4, 1200.00, 3300.00, 280),

    # Data & AI Infrastructure
    ('DAI-501', 'Enterprise Vector Database Node', 5, 2400.00, 4800.00, 160),
    ('DAI-502', 'Data Lakehouse Streaming Engine', 5, 3200.00, 6200.00, 130),
    ('DAI-503', 'GPU Cluster Inference Appliance (Dual A100)', 5, 8500.00, 13500.00, 50),
    ('DAI-504', 'Real-Time ETL Ingestion Pipeline Connector', 5, 750.00, 1650.00, 300),
    ('DAI-505', 'Automated Data Governance & Lineage Hub', 5, 1400.00, 2900.00, 200)
]

SALES_REPS_SPEC = [
    ('REP-001', 'Sarah Jenkins', 's.jenkins@enterprise.com', 1, 750000.00, '2021-03-15'),
    ('REP-002', 'Michael Chang', 'm.chang@enterprise.com', 1, 650000.00, '2021-08-01'),
    ('REP-003', 'Emily Rodriguez', 'e.rodriguez@enterprise.com', 1, 700000.00, '2022-02-10'),
    ('REP-004', 'David Vance', 'd.vance@enterprise.com', 2, 850000.00, '2020-05-12'),
    ('REP-005', 'Jessica Taylor', 'j.taylor@enterprise.com', 2, 800000.00, '2021-11-20'),
    ('REP-006', 'Kevin O\'Connor', 'k.oconnor@enterprise.com', 2, 900000.00, '2020-01-18'),
    ('REP-007', 'Amanda Miller', 'a.miller@enterprise.com', 3, 600000.00, '2022-06-01'),
    ('REP-008', 'Brian Patel', 'b.patel@enterprise.com', 3, 580000.00, '2022-09-15'),
    ('REP-009', 'Rachel Hayes', 'r.hayes@enterprise.com', 3, 620000.00, '2023-01-10'),
    ('REP-010', 'Marcus Washington', 'm.washington@enterprise.com', 4, 720000.00, '2021-04-05'),
    ('REP-011', 'Laura Bennett', 'l.bennett@enterprise.com', 4, 680000.00, '2022-07-22'),
    ('REP-012', 'Daniel Foster', 'd.foster@enterprise.com', 4, 740000.00, '2021-10-30')
]

def generate_all_data():
    """Generates 10,000+ customers and 30,000+ orders with realistic distributions."""
    print("[*] Generating realistic Enterprise synthetic dataset...")

    # 1. Regions DataFrame
    df_regions = pd.DataFrame(REGIONS_DATA)
    df_regions.to_csv(RAW_DATA_DIR / 'regions.csv', index=False)

    # 2. Categories DataFrame
    df_categories = pd.DataFrame(CATEGORIES_DATA)
    df_categories.to_csv(RAW_DATA_DIR / 'categories.csv', index=False)

    # 3. Products DataFrame
    products_list = []
    for idx, (sku, name, cat_id, cost, price, stock) in enumerate(PRODUCTS_SPEC, start=1):
        margin = round(((price - cost) / price) * 100, 2)
        products_list.append({
            'product_id': idx,
            'product_sku': sku,
            'product_name': name,
            'category_id': cat_id,
            'unit_cost': cost,
            'unit_price': price,
            'target_margin_pct': margin,
            'stock_quantity': stock,
            'is_discontinued': False
        })
    df_products = pd.DataFrame(products_list)
    df_products.to_csv(RAW_DATA_DIR / 'products.csv', index=False)

    # 4. Sales Reps DataFrame
    sales_reps_list = []
    for idx, (code, name, email, reg_id, quota, hire_date) in enumerate(SALES_REPS_SPEC, start=1):
        sales_reps_list.append({
            'rep_id': idx,
            'rep_code': code,
            'rep_name': name,
            'email': email,
            'region_id': reg_id,
            'quota_annual': quota,
            'hire_date': hire_date,
            'is_active': True
        })
    df_sales_reps = pd.DataFrame(sales_reps_list)
    df_sales_reps.to_csv(RAW_DATA_DIR / 'sales_reps.csv', index=False)

    # 5. Customers Generation (10,500 realistic records)
    print(f"[*] Generating {NUM_CUSTOMERS} customers...")
    customers_list = []
    region_weights = [0.32, 0.35, 0.15, 0.18] # West & East have higher tech density

    for i in range(1, NUM_CUSTOMERS + 1):
        c_code = f"CUST-{i:05d}"
        c_name = fake.name()
        c_company = fake.company() if random.random() > 0.15 else None
        c_email = f"user_{i}@{fake.domain_name()}"
        c_region = np.random.choice([1, 2, 3, 4], p=region_weights)
        
        # Signup dates distributed between 2023-01-01 and 2026-06-01
        days_span = (datetime(2026, 6, 1) - START_DATE).days
        signup_dt = START_DATE + timedelta(days=random.randint(0, days_span))
        
        customers_list.append({
            'customer_id': i,
            'customer_code': c_code,
            'customer_name': c_name,
            'email': c_email,
            'company_name': c_company,
            'region_id': c_region,
            'signup_date': signup_dt.strftime('%Y-%m-%d'),
            'segment': 'Standard', # will be populated in ETL/analytics
            'is_active': True
        })

    df_customers = pd.DataFrame(customers_list)
    df_customers.to_csv(RAW_DATA_DIR / 'customers.csv', index=False)

    # 6. Orders Generation (32,000 orders across time with seasonality and customer repeats)
    print(f"[*] Generating {NUM_ORDERS} orders & associated line items...")
    orders_list = []
    order_items_list = []
    item_id_counter = 1

    # Map reps by region for realistic assignment
    reps_by_region = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    # High frequency repeat customers vs single buyers
    customer_ids = list(range(1, NUM_CUSTOMERS + 1))
    
    # 20% are frequent buyers (take 60% of orders), 80% are occasional
    frequent_buyers = random.sample(customer_ids, int(NUM_CUSTOMERS * 0.20))
    occasional_buyers = [cid for cid in customer_ids if cid not in frequent_buyers]

    order_statuses = ['Completed', 'Completed', 'Completed', 'Completed', 'Shipped', 'Processing', 'Cancelled', 'Returned']
    status_weights = [0.82, 0.05, 0.04, 0.03, 0.02, 0.01, 0.015, 0.015] # Most completed

    payment_methods = ['Credit Card', 'Wire Transfer', 'ACH Payment', 'Corporate Invoicing']
    payment_weights = [0.50, 0.25, 0.15, 0.10]

    # Pre-build customer lookup for region and signup date
    cust_lookup = {c['customer_id']: (c['region_id'], datetime.strptime(c['signup_date'], '%Y-%m-%d')) for c in customers_list}

    total_days = (END_DATE - START_DATE).days

    for order_idx in range(1, NUM_ORDERS + 1):
        order_number = f"ORD-{2023 + (order_idx % 4)}-{order_idx:06d}"
        
        # Select customer
        if random.random() < 0.65:
            cid = random.choice(frequent_buyers)
        else:
            cid = random.choice(occasional_buyers)

        c_region, c_signup = cust_lookup[cid]
        rep_id = random.choice(reps_by_region[c_region])

        # Date generation after customer signup date with seasonal Q4 multiplier
        earliest_day = max(0, (c_signup - START_DATE).days)
        random_day = random.randint(earliest_day, total_days)
        order_dt = START_DATE + timedelta(days=random_day)

        # Seasonality: Q4 (Oct-Dec) higher sales
        month = order_dt.month
        status = np.random.choice(order_statuses, p=status_weights)
        is_returned = (status == 'Returned')

        pay_method = np.random.choice(payment_methods, p=payment_weights)
        shipping_cost = round(random.choice([0.0, 15.0, 25.0, 50.0, 120.0]), 2)

        # Generate 1 to 4 line items per order
        num_items = np.random.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.10, 0.05])
        selected_prods = random.sample(products_list, num_items)

        order_subtotal = 0.0
        order_cost = 0.0
        order_discount = 0.0

        for prod in selected_prods:
            qty = np.random.choice([1, 2, 3, 5, 10], p=[0.65, 0.20, 0.08, 0.05, 0.02])
            u_price = prod['unit_price']
            u_cost = prod['unit_cost']
            
            # Realistic discount: 0% mostly, occasional 5-20%
            disc_pct = np.random.choice([0.0, 5.0, 10.0, 15.0, 20.0, 25.0], p=[0.55, 0.18, 0.14, 0.08, 0.04, 0.01])
            gross_item = u_price * qty
            item_disc_val = round(gross_item * (disc_pct / 100.0), 2)
            net_item_amount = round(gross_item - item_disc_val, 2)
            total_item_cost = round(u_cost * qty, 2)
            item_profit = round(net_item_amount - total_item_cost, 2)
            item_margin = round((item_profit / net_item_amount) * 100, 2) if net_item_amount > 0 else 0.0

            order_items_list.append({
                'item_id': item_id_counter,
                'order_id': order_idx,
                'product_id': prod['product_id'],
                'quantity': int(qty),
                'unit_price': float(u_price),
                'unit_cost': float(u_cost),
                'discount_pct': float(disc_pct),
                'item_total_amount': float(net_item_amount),
                'item_total_cost': float(total_item_cost),
                'item_profit': float(item_profit),
                'item_margin_pct': float(item_margin),
                'is_returned': is_returned
            })
            item_id_counter += 1

            order_subtotal += gross_item
            order_discount += item_disc_val
            order_cost += total_item_cost

        order_total = round(order_subtotal - order_discount + shipping_cost, 2)
        order_net_profit = round(order_total - order_cost, 2)
        order_margin = round((order_net_profit / order_total) * 100, 2) if order_total > 0 else 0.0

        orders_list.append({
            'order_id': order_idx,
            'order_number': order_number,
            'customer_id': cid,
            'rep_id': rep_id,
            'region_id': c_region,
            'order_date': order_dt.strftime('%Y-%m-%d'),
            'status': status,
            'payment_method': pay_method,
            'shipping_cost': shipping_cost,
            'subtotal_amount': round(order_subtotal, 2),
            'discount_amount': round(order_discount, 2),
            'total_amount': order_total,
            'total_cost': round(order_cost, 2),
            'net_profit': order_net_profit,
            'profit_margin_pct': order_margin,
            'is_returned': is_returned
        })

    df_orders = pd.DataFrame(orders_list)
    df_orders.to_csv(RAW_DATA_DIR / 'orders.csv', index=False)

    df_order_items = pd.DataFrame(order_items_list)
    df_order_items.to_csv(RAW_DATA_DIR / 'order_items.csv', index=False)

    print(f"[+] Successfully generated raw dataset:")
    print(f"    - Customers:   {len(df_customers):,}")
    print(f"    - Orders:      {len(df_orders):,}")
    print(f"    - Order Items: {len(df_order_items):,}")
    print(f"    - Products:    {len(df_products):,}")
    print(f"    - Sales Reps:  {len(df_sales_reps):,}")
    print(f"    - Regions:     {len(df_regions):,}")

if __name__ == '__main__':
    generate_all_data()
