-- ====================================================================
-- Enterprise Sales & Customer Intelligence Platform
-- Advanced Sales & Trend Analytics SQL Queries
-- Includes: MoM & YoY Growth, Moving Averages, Rep Quota Attainment
-- ====================================================================

-- 1. Monthly Revenue, Profit, and Month-over-Month (MoM) Growth Analysis
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS monthly_revenue,
        ROUND(SUM(total_cost), 2) AS monthly_cost,
        ROUND(SUM(net_profit), 2) AS monthly_profit,
        ROUND((SUM(net_profit) / NULLIF(SUM(total_amount), 0)) * 100, 2) AS monthly_profit_margin_pct
    FROM orders
    WHERE status != 'Cancelled'
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    sales_month,
    total_orders,
    monthly_revenue,
    monthly_profit,
    monthly_profit_margin_pct,
    LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) 
        / NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY sales_month), 0)) * 100, 
        2
    ) AS mom_revenue_growth_pct,
    ROUND(
        AVG(monthly_revenue) OVER (ORDER BY sales_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        2
    ) AS rolling_3_month_avg_revenue
FROM MonthlySales
ORDER BY sales_month ASC;

-- 2. Regional Sales & Profit Share with Window SUM()
SELECT 
    r.region_name,
    COUNT(DISTINCT o.order_id) AS total_regional_orders,
    ROUND(SUM(o.total_amount), 2) AS regional_revenue,
    ROUND(SUM(o.net_profit), 2) AS regional_profit,
    ROUND((SUM(o.net_profit) / NULLIF(SUM(o.total_amount), 0)) * 100, 2) AS regional_margin_pct,
    ROUND(
        (SUM(o.total_amount) / SUM(SUM(o.total_amount)) OVER ()) * 100, 
        2
    ) AS market_revenue_share_pct
FROM regions r
JOIN orders o ON r.region_id = o.region_id
WHERE o.status != 'Cancelled'
GROUP BY r.region_id, r.region_name
ORDER BY regional_revenue DESC;

-- 3. Sales Representative Quota Attainment Leaderboard
SELECT 
    sr.rep_code,
    sr.rep_name,
    r.region_name,
    sr.quota_annual,
    ROUND(SUM(o.total_amount), 2) AS actual_revenue_generated,
    ROUND(SUM(o.net_profit), 2) AS actual_profit_generated,
    ROUND((SUM(o.total_amount) / NULLIF(sr.quota_annual, 0)) * 100, 2) AS quota_attainment_pct,
    CASE 
        WHEN (SUM(o.total_amount) / NULLIF(sr.quota_annual, 0)) >= 1.0 THEN 'Quota Exceeded'
        WHEN (SUM(o.total_amount) / NULLIF(sr.quota_annual, 0)) >= 0.80 THEN 'On Track'
        ELSE 'Underperforming'
    END AS performance_status
FROM sales_reps sr
JOIN regions r ON sr.region_id = r.region_id
LEFT JOIN orders o ON sr.rep_id = o.rep_id AND o.status != 'Cancelled'
GROUP BY sr.rep_id, sr.rep_code, sr.rep_name, r.region_name, sr.quota_annual
ORDER BY actual_revenue_generated DESC;
