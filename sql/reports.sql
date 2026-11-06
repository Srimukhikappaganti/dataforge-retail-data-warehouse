-- 1. Revenue by product category
SELECT p.category,
       SUM(f.quantity) AS units_sold,
       ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 2. Monthly revenue
SELECT d.year,
       d.month,
       ROUND(SUM(f.revenue), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Top customers by revenue
SELECT c.customer_name,
       c.city,
       ROUND(SUM(f.revenue), 2) AS customer_revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_key, c.customer_name, c.city
ORDER BY customer_revenue DESC
LIMIT 5;

-- 4. Product performance
SELECT p.product_name,
       p.category,
       SUM(f.quantity) AS units_sold,
       ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY revenue DESC;
