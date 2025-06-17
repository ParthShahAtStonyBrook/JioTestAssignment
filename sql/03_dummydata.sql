-- Generate 20 orders per user with items
DO $$
DECLARE
    u RECORD;
    i INT;
    new_order_id INT;
BEGIN
    FOR u IN SELECT id, username FROM users WHERE username IN ('user1', 'user2', 'user3') LOOP
        FOR i IN 1..20 LOOP
            -- Insert order
            INSERT INTO orders (user_id, date, status)
            VALUES (u.id, CURRENT_TIMESTAMP - (i || ' hours')::interval, 
                    CASE WHEN i % 2 = 0 THEN 'completed' ELSE 'pending' END)
            RETURNING id INTO new_order_id;

            -- Insert order items
            INSERT INTO order_items (order_id, name, quantity, price)
            VALUES 
              (new_order_id, 'Product A', 1, 99.99),
              (new_order_id, 'Product B', 2, 49.50);
        END LOOP;
    END LOOP;
END
$$;
