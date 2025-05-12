from tkinter import *
from connect import connect_database
from tkinter import messagebox
from firebase_config import tax_in_firebase

def save_tax(tax_count):
    try:
        tax = float(tax_count.get())  # Validate input
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for tax.")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_dbms')
        
        # Call the function to execute the SQL from the file

        # Insert or update the tax value
        cursor.execute('REPLACE INTO tax_data (id, tax) VALUES (1, %s)', (tax,))
        connection.commit()
        tax_in_firebase(tax)
        tax_dashboard.destroy()
        messagebox.showinfo("Success", f"Tax rate of {tax}% saved successfully.")
        
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        connection.close()
def calculate_product_value(product_id):
    try:
        product_id = int(product_id)
        cursor, connection = connect_database()
        if not cursor or not connection:
            return None

        # Convert to integer to avoid SQL error if passed from GUI
        product_id = int(product_id)

        cursor.execute('SELECT calculate_product_value_by_id(%s)', (product_id,))
        result = cursor.fetchone()

        return result[0] if result and result[0] is not None else None

    except Exception as e:
        print(f"Error in calculating product value: {e}")
        return None

    finally:
        if connection:
            connection.close()



def tax_form(dashboard):
    global tax_dashboard
    tax_dashboard = Toplevel()
    tax_dashboard.title('Tax Dashboard')
    tax_dashboard.geometry('400x400')
    tax_dashboard.resizable(0, 0)
    tax_dashboard.grab_set()

    # Tax entry
    Label(tax_dashboard, text='Enter Tax Percentage (%)', font=12).pack(pady=(30, 10))
    tax_spinbox = Spinbox(tax_dashboard, from_=0, to=100, font=12)
    tax_spinbox.pack(pady=5)

    Button(tax_dashboard, text='Save Tax', font=12, bg='#2B7075', fg='white', width=15,
           command=lambda: save_tax(tax_spinbox)).pack(pady=15)

    # Product ID entry
    Label(tax_dashboard, text='Enter Product ID', font=12).pack(pady=(30, 10))
    product_id_entry = Entry(tax_dashboard, font=12)
    product_id_entry.pack(pady=5)

    # Result display
    result_label = Label(tax_dashboard, text='', font=12, fg='blue')
    result_label.pack(pady=10)

    # Wrapper to display result in label
    def show_product_value():
        product_id = product_id_entry.get()
        value = calculate_product_value(product_id)
        if value is not None:
            result_label.config(text=f"Product Value: {value}")
        else:
            result_label.config(text="Product not found or error occurred.")

    Button(tax_dashboard, text='Calculate Product Value', font=12, bg='#2B7075', fg='white', width=20,
           command=show_product_value).pack(pady=10)
