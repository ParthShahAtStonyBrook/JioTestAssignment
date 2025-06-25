DO $$
DECLARE
    u RECORD;
    i INT;
    new_order_id INT;
    price_a NUMERIC;
    price_b NUMERIC;
BEGIN
    FOR u IN SELECT id, username FROM users WHERE username IN ('user1', 'user2', 'user3') LOOP
        FOR i IN 1..20 LOOP
            -- Insert order with different date (i days ago)
            INSERT INTO orders (user_id, date, status)
            VALUES (
                u.id,
                CURRENT_DATE - (i || ' days')::interval,  -- Use date offset
                CASE WHEN i % 2 = 0 THEN 'completed' ELSE 'pending' END
            )
            RETURNING id INTO new_order_id;

            -- Generate varying prices
            price_a := 80 + (random() * 40);  -- 80.00 to 120.00
            price_b := 30 + (random() * 20);  -- 30.00 to 50.00

            -- Insert order items
            INSERT INTO order_items (order_id, name, quantity, price)
            VALUES 
              (new_order_id, 'Product A', 1, ROUND(price_a, 2)),
              (new_order_id, 'Product B', 2, ROUND(price_b, 2));
        END LOOP;
    END LOOP;
END
$$;
