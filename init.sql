-- Create tables
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data from the frontend
INSERT INTO orders (id, date, status) VALUES
    (1, '2025-06-01', 'Delivered'),
    (2, '2025-05-28', 'Delivered'),
    (3, '2025-05-25', 'Delivered');

INSERT INTO order_items (id, order_id, name, price) VALUES
    (101, 1, 'Wireless Headphones', 99.99),
    (102, 1, 'Smart Watch', 199.99),
    (201, 2, 'Laptop Stand', 49.99),
    (202, 2, 'Keyboard', 79.99),
    (301, 3, 'Monitor', 299.99);

-- Insert sample user (password: admin123)
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', 'pbkdf2:sha256:600000$7qyqVa4vQxlG9Xm2$c1a85b80a7c77c66c878a8d1bff246e9c6140f37b44a9f4b197e1c1963d776df'); 