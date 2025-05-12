import pymysql
from pymysql import OperationalError
from datetime import datetime
from connect import connect_database

def log_employee_login(username):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        # Call the procedure with the emp_id (username in this case)
        cursor.execute('CALL log_employee_login(%s)', (username,))  # Using %s as placeholder for emp_id
        connection.commit()
        print('Employee login logged successfully.')

    except Exception as e:
        print(f"Error logging employee login: {e}")
        connection.rollback()
    finally:
        connection.close()

# Function to create the 'after_product_delete' trigger
def create_product_delete_trigger():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        # Define the SQL for creating the trigger
        trigger_sql = """

        CREATE TRIGGER after_product_delete
        AFTER DELETE ON product_details
        FOR EACH ROW
        BEGIN
            INSERT INTO activity_log (activity_type, reference_id, activity_time)
            VALUES ('Product Deleted', OLD.product_id, NOW());
        END;
        """

        # Execute trigger creation query
        cursor.execute(trigger_sql)
        connection.commit()
        print('Trigger after_product_delete created successfully.')

    except Exception as e:
        print(f"Error creating trigger: {e}")
        connection.rollback()
    finally:
        connection.close()

# Function to create a function that returns formatted timestamps
def create_get_formatted_timestamp_function():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        # Define the SQL for creating the function
        function_sql = """
            CREATE FUNCTION get_formatted_timestamp()
            RETURNS VARCHAR(100)
            DETERMINISTIC
            BEGIN
                RETURN DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');
            END;
        """

        # Execute function creation query
        cursor.execute(function_sql)
        connection.commit()
        print('Function get_formatted_timestamp created successfully.')

    except Exception as e:
        print(f"Error creating function: {e}")
        connection.rollback()
    finally:
        connection.close()

# Function to create a procedure for logging employee login
def create_log_employee_login_procedure():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        # Define the SQL for creating the procedure
        procedure_sql = """
        CREATE PROCEDURE log_employee_login(emp_id INT)
        BEGIN
            INSERT INTO activity_log (activity_type, reference_id, activity_time)
            VALUES ('Login', emp_id, NOW());
        END ;
        """

        # Execute procedure creation query
        cursor.execute(procedure_sql)
        connection.commit()
        print('Procedure log_employee_login created successfully.')

    except Exception as e:
        print(f"Error creating procedure: {e}")
        connection.rollback()
    finally:
        connection.close()

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


# Example function to call and test the trigger, function, and procedure
def create_all_triggers_functions_and_procedures():
    # Create the trigger for product deletion
    create_product_delete_trigger()
    
    # Create the function for formatted timestamp
    create_get_formatted_timestamp_function()
    
    # Create the procedure for employee login
    create_log_employee_login_procedure()
    create_calculate_product_value_function_by_id()

# Call this function in your main flow to create all triggers, functions, and procedures
create_all_triggers_functions_and_procedures()

