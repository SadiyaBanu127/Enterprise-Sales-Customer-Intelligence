-- ====================================================================
-- Enterprise Sales & Customer Intelligence Platform
-- Advanced Profitability & Margin Optimization SQL Queries
-- Includes: Profitability Matrix, Discount Elasticity, Loss Leaders
-- ====================================================================

-- 1. Product Profitability 4-Quadrant Matrix Classification
WITH ProductSalesMetrics AS (
    SELECT 
        p.product_id,
        p.product_sku,
        p.product_name,
        c.category_name,
        p.unit_cost,
        p.unit_price,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.item_total_amount), 2) AS total_revenue,
        ROUND(SUM(oi.item_profit), 2) AS total_profit,
        ROUND((SUM(oi.item_profit) / NULLIF(SUM(oi.item_total_amount), 0)) * 100, 2) AS realized_margin_pct,
        ROUND(AVG(oi.discount_pct), 2) AS avg_discount_pct
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != 'Cancelled'
    GROUP BY p.product_id, p.product_sku, p.product_name, c.category_name, p.unit_cost, p.unit_price
),
Averages AS (
    SELECT 
        AVG(total_revenue) AS avg_benchmark_revenue,
        AVG(total_profit) AS avg_benchmark_profit
    FROM ProductSalesMetrics
)
SELECT 
    psm.product_sku,
    psm.product_name,
    psm.category_name,
    psm.total_units_sold,
    psm.total_revenue,
    psm.total_profit,
    psm.realized_margin_pct,
    psm.avg_discount_pct,
    CASE 
        WHEN psm.total_revenue >= a.avg_benchmark_revenue AND psm.total_profit >= a.avg_benchmark_profit 
            THEN 'Star Performers (High Rev, High Profit)'
        WHEN psm.total_revenue >= a.avg_benchmark_revenue AND psm.total_profit < a.avg_benchmark_profit 
            THEN 'Volume Drivers / Low Margin (High Rev, Low Profit)'
        WHEN psm.total_revenue < a.avg_benchmark_revenue AND psm.total_profit >= a.avg_benchmark_profit 
            THEN 'Niche High Margin (Low Rev, High Profit)'
        ELSE 'Underperformers (Low Rev, Low Profit)'
    END AS profitability_quadrant,
    CASE 
        WHEN psm.avg_discount_pct > 15.0 AND psm.realized_margin_pct < 20.0 
            THEN 'Immediate Action: Curtail heavy discounting'
        WHEN psm.total_profit >= a.avg_benchmark_profit 
            THEN 'Maintain pricing power & expand distribution'
        ELSE 'Review COGS or phase out SKU'
    END AS strategic_recommendation
FROM ProductSalesMetrics psm
CROSS JOIN Averages a
ORDER BY psm.total_revenue DESC;

-- 2. Discount Leakage & Negative Margin Audit
SELECT 
    o.order_number,
    o.order_date,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    oi.item_total_amount,
    oi.item_total_cost,
    oi.item_profit,
    oi.item_margin_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE oi.item_profit < 0 OR oi.discount_pct > 20.0
ORDER BY oi.item_profit ASC
LIMIT 50;
