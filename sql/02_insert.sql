-- Insert a sample admin user (with password 'admin123')
INSERT INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:260000$Ma7xihHWjJJwZ7fP$304eea29adc8f3c82d9df1338b1ea8eda26088640ec746ed536d2edca1dd712e')
ON CONFLICT (username) DO NOTHING;

-- Insert sample orders for the admin user
INSERT INTO orders (user_id, date, status)
SELECT id, CURRENT_TIMESTAMP - interval '1 day', 'completed'
FROM users WHERE username = 'admin'
RETURNING id;

-- Insert sample order items
INSERT INTO order_items (order_id, name, quantity, price)
SELECT 
    o.id,
    'Smartphone X',
    2,
    999.99
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.username = 'admin'
LIMIT 1;

-- Insert another order
INSERT INTO orders (user_id, date, status)
SELECT id, CURRENT_TIMESTAMP - interval '2 hours', 'pending'
FROM users WHERE username = 'admin'
RETURNING id;

-- Insert items for the second order
INSERT INTO order_items (order_id, name, quantity, price)
SELECT 
    o.id,
    'Laptop Pro',
    1,
    1499.99
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.username = 'admin'
ORDER BY o.date DESC
LIMIT 1; 