-- Delete existing orders and order items for specific users
DO $$
DECLARE
    user_ids INT[];
BEGIN
    -- Get user IDs
    SELECT array_agg(id) INTO user_ids FROM users WHERE username IN ('user1', 'user2', 'user3');

    -- Delete order_items first to maintain foreign key integrity
    DELETE FROM order_items WHERE order_id IN (
        SELECT id FROM orders WHERE user_id = ANY(user_ids)
    );

    -- Delete the orders
    DELETE FROM orders WHERE user_id = ANY(user_ids);
END
$$;
