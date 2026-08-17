-- ====================================================================
-- Enterprise Sales & Customer Intelligence Platform
-- Advanced Customer Analytics SQL Queries
-- Includes: RFM Segmentation, CLV, Retention Cohorts, Window Functions
-- ====================================================================

-- 1. Full RFM (Recency, Frequency, Monetary) Scoring with NTILE() Window Functions
WITH CustomerAggregates AS (
    SELECT 
        c.customer_id,
        c.customer_code,
        c.customer_name,
        r.region_name,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0.00) AS total_monetary_spend,
        COALESCE(AVG(o.total_amount), 0.00) AS avg_order_value,
        MAX(o.order_date) AS last_order_date,
        DATEDIFF('2026-08-01', MAX(o.order_date)) AS recency_days
    FROM customers c
    JOIN regions r ON c.region_id = r.region_id
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'Cancelled'
    GROUP BY c.customer_id, c.customer_code, c.customer_name, r.region_name
),
RFM_Tiers AS (
    SELECT 
        customer_id,
        customer_code,
        customer_name,
        region_name,
        total_orders,
        total_monetary_spend,
        avg_order_value,
        recency_days,
        -- Score 5 is best (most recent / highest spend)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY total_monetary_spend ASC) AS m_score
    FROM CustomerAggregates
)
SELECT 
    customer_id,
    customer_code,
    customer_name,
    region_name,
    total_orders,
    total_monetary_spend,
    avg_order_value,
    recency_days,
    r_score,
    f_score,
    m_score,
    (r_score * 100 + f_score * 10 + m_score) AS rfm_combined_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        ELSE 'Lost Customers'
    END AS calculated_segment
FROM RFM_Tiers
ORDER BY total_monetary_spend DESC;

-- 2. Customer Lifetime Value (CLV) and Retention Cohorts
SELECT 
    DATE_FORMAT(c.signup_date, '%Y-%m') AS cohort_month,
    COUNT(DISTINCT c.customer_id) AS total_cohort_customers,
    COUNT(DISTINCT CASE WHEN c.total_orders_count > 1 THEN c.customer_id END) AS repeat_customers,
    ROUND(COUNT(DISTINCT CASE WHEN c.total_orders_count > 1 THEN c.customer_id END) * 100.0 / COUNT(DISTINCT c.customer_id), 2) AS repeat_purchase_rate_pct,
    ROUND(SUM(c.total_spend), 2) AS cohort_total_revenue,
    ROUND(AVG(c.total_spend), 2) AS avg_clv_per_customer
FROM customers c
GROUP BY DATE_FORMAT(c.signup_date, '%Y-%m')
ORDER BY cohort_month ASC;

-- 3. Top 10 Enterprise Customers with Running Cumulative Contribution
WITH RankedCustomers AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.company_name,
        r.region_name,
        SUM(o.total_amount) AS customer_revenue,
        SUM(o.net_profit) AS customer_profit,
        ROUND((SUM(o.net_profit) / NULLIF(SUM(o.total_amount), 0)) * 100, 2) AS profit_margin_pct
    FROM customers c
    JOIN regions r ON c.region_id = r.region_id
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'Cancelled'
    GROUP BY c.customer_id, c.customer_name, c.company_name, r.region_name
)
SELECT 
    customer_id,
    customer_name,
    company_name,
    region_name,
    customer_revenue,
    customer_profit,
    profit_margin_pct,
    DENSE_RANK() OVER (ORDER BY customer_revenue DESC) AS revenue_rank,
    ROUND(SUM(customer_revenue) OVER (ORDER BY customer_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue
FROM RankedCustomers
LIMIT 10;
