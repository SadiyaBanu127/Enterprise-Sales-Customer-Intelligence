-- =========================================================
-- Enterprise Sales & Customer Intelligence Platform
-- Relational Database Schema (MySQL & ANSI SQL Compliant)
-- =========================================================

-- Disable foreign key checks for clean dropping/creation if needed
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Users Table (Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst', -- 'admin' or 'analyst'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Regions Table
CREATE TABLE IF NOT EXISTS regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE,
    country VARCHAR(50) NOT NULL DEFAULT 'United States',
    market_tier VARCHAR(20) DEFAULT 'Tier 1',
    target_growth_rate DECIMAL(5,2) DEFAULT 12.50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_region_name (region_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Sales Representatives Table
CREATE TABLE IF NOT EXISTS sales_reps (
    rep_id INT AUTO_INCREMENT PRIMARY KEY,
    rep_code VARCHAR(20) NOT NULL UNIQUE,
    rep_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    region_id INT NOT NULL,
    quota_annual DECIMAL(12,2) NOT NULL DEFAULT 500000.00,
    hire_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE CASCADE,
    INDEX idx_rep_region (region_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Product Categories Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(80) NOT NULL UNIQUE,
    description TEXT,
    target_margin DECIMAL(5,2) DEFAULT 25.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cat_name (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_sku VARCHAR(30) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    target_margin_pct DECIMAL(5,2) GENERATED ALWAYS AS (ROUND(((unit_price - unit_cost) / unit_price) * 100, 2)) STORED,
    stock_quantity INT NOT NULL DEFAULT 100,
    is_discontinued BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
    INDEX idx_prod_category (category_id),
    INDEX idx_prod_sku (product_sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(30) NOT NULL UNIQUE,
    customer_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL,
    company_name VARCHAR(120),
    segment VARCHAR(50) DEFAULT 'Standard', -- 'Champions', 'Loyal Customers', 'Potential Loyalists', 'New Customers', 'At Risk', 'Lost'
    region_id INT NOT NULL,
    signup_date DATE NOT NULL,
    total_orders_count INT DEFAULT 0,
    total_spend DECIMAL(12,2) DEFAULT 0.00,
    average_order_value DECIMAL(10,2) DEFAULT 0.00,
    last_purchase_date DATE,
    recency_days INT DEFAULT 0,
    frequency_score INT DEFAULT 1,
    monetary_score INT DEFAULT 1,
    recency_score INT DEFAULT 1,
    rfm_score INT DEFAULT 111,
    churn_risk_score DECIMAL(5,4) DEFAULT 0.0000,
    churn_risk_level VARCHAR(20) DEFAULT 'Low Risk', -- 'Low Risk', 'Medium Risk', 'High Risk'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE RESTRICT,
    INDEX idx_cust_region (region_id),
    INDEX idx_cust_segment (segment),
    INDEX idx_cust_churn (churn_risk_level),
    INDEX idx_cust_rfm (rfm_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(40) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    rep_id INT,
    region_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Completed', -- 'Completed', 'Shipped', 'Processing', 'Cancelled', 'Returned'
    payment_method VARCHAR(50) DEFAULT 'Credit Card',
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    subtotal_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_cost DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    net_profit DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    profit_margin_pct DECIMAL(5,2) DEFAULT 0.00,
    is_returned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (rep_id) REFERENCES sales_reps(rep_id) ON DELETE SET NULL,
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE RESTRICT,
    INDEX idx_order_date (order_date),
    INDEX idx_order_customer (customer_id),
    INDEX idx_order_region (region_id),
    INDEX idx_order_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    discount_pct DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    item_total_amount DECIMAL(12,2) NOT NULL,
    item_total_cost DECIMAL(12,2) NOT NULL,
    item_profit DECIMAL(12,2) NOT NULL,
    item_margin_pct DECIMAL(5,2) NOT NULL,
    is_returned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_item_order (order_id),
    INDEX idx_item_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. ML Predictions Audit Table (Customer Churn Logs)
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    model_name VARCHAR(80) NOT NULL DEFAULT 'RandomForestClassifier_v1',
    churn_probability DECIMAL(5,4) NOT NULL,
    predicted_risk_level VARCHAR(20) NOT NULL,
    key_drivers JSON,
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    INDEX idx_pred_cust (customer_id),
    INDEX idx_pred_risk (predicted_risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Time-Series Forecasts Cache Table
CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id INT AUTO_INCREMENT PRIMARY KEY,
    forecast_date DATE NOT NULL,
    horizon_days INT NOT NULL, -- 30, 90, 180
    model_type VARCHAR(50) NOT NULL DEFAULT 'HoltWinters_Additive',
    predicted_revenue DECIMAL(14,2) NOT NULL,
    lower_ci_95 DECIMAL(14,2) NOT NULL,
    upper_ci_95 DECIMAL(14,2) NOT NULL,
    growth_rate_pct DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_forecast_date (forecast_date),
    INDEX idx_forecast_horizon (horizon_days)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
