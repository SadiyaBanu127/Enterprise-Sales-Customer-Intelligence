-- =========================================================
-- Enterprise Sales & Customer Intelligence Platform
-- Base Seed Script (Default Accounts, Categories, Regions)
-- =========================================================

-- 1. Default Users (Pass: 'Admin@123' and 'Analyst@123' hashed with pbkdf2:sha256 / scrypt)
-- Admin: admin@enterprise.com / Admin@123
-- Analyst: analyst@enterprise.com / Analyst@123
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES 
('admin', 'admin@enterprise.com', 'scrypt:32768:8:1$u7lq8fWJzGkZq1xX$a827464010ff75846ff9ba7c5bb17baab5ebdfd1eeef8bfa17cff17e92ae4c1e4ceeb3bf2fc26c7104b207ee7b2cf3a77fc9a4fa430b0e5ee600642db4d94b0d', 'System Administrator', 'admin', 1),
('analyst', 'analyst@enterprise.com', 'scrypt:32768:8:1$7U6rI9b0iUfJq8zZ$6dafe737c352ffb6ee0895c102a0a2df3351980cae6cf45c60fbcfec0ceefdaef7fa364c7feefcba5bb47164ffbf9cf308b265d6c81eece39f99f36f3322ce6e', 'Senior Lead Analyst', 'analyst', 1)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- 2. Regions
INSERT INTO regions (region_id, region_name, country, market_tier, target_growth_rate)
VALUES 
(1, 'North America - East', 'United States', 'Tier 1', 14.50),
(2, 'North America - West', 'United States', 'Tier 1', 18.00),
(3, 'North America - Central', 'United States', 'Tier 2', 11.00),
(4, 'North America - South', 'United States', 'Tier 2', 15.20)
ON DUPLICATE KEY UPDATE market_tier=VALUES(market_tier);

-- 3. Product Categories
INSERT INTO categories (category_id, category_name, description, target_margin)
VALUES
(1, 'Enterprise Cloud Software', 'SaaS subscriptions, enterprise licenses, AI developer seats', 78.50),
(2, 'Hardware & Servers', 'Rackmount servers, edge compute units, high-performance switches', 32.00),
(3, 'Professional Services', 'Implementation consulting, data migration, security audits', 55.00),
(4, 'Cybersecurity Solutions', 'Endpoint protection, SIEM infrastructure, zero-trust gateways', 68.00),
(5, 'Data & AI Infrastructure', 'Vector DB appliances, GPU clusters, data lakehouse integrations', 48.00)
ON DUPLICATE KEY UPDATE target_margin=VALUES(target_margin);
