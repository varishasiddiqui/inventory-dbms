def create_calculate_product_value_function_by_id():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        function_sql = """
        CREATE FUNCTION calculate_product_value_by_id(pid INT)
        RETURNS DECIMAL(10,2)
        DETERMINISTIC
        READS SQL DATA
        BEGIN
            DECLARE product_price DECIMAL(10,2);
            DECLARE product_quantity INT;
            DECLARE total_value DECIMAL(10,2);

            SELECT price, quantity INTO product_price, product_quantity
            FROM product_details
            WHERE product_id = pid;

            SET total_value = product_price * product_quantity;
            RETURN total_value;
        END;
        """
        cursor.execute(function_sql)
        connection.commit()
        print('Function calculate_product_value_by_id created successfully.')

    except Exception as e:
        print(f"Error creating function: {e}")
        connection.rollback()
    finally:
        connection.close()
