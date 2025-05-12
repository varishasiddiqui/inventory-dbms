from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
import os
from decimal import Decimal
from connect import connect_database
def count_sales():
    cursor,connection=connect_database()
    cursor.execute('SELECT COUNT(*) FROM sales_data')
    result=cursor.fetchone()
    return result[0]

def save_sales_to_db(cart_list, invoice, customer_name, contact):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('use inventory_dbms')
        cursor.execute(' select tax from tax_data')
        tax_percent = cursor.fetchone()[0]
        payment_mode = "Cash"  # or from dropdown
        emp_name = "Admin"  # or from login

        for product in cart_list:
            product_id = product[0]
            product_name = product[1]
            
            unit_price = Decimal(product[2])
            discount_percent = Decimal(product[3]) if product[3] else Decimal('0.0')
            quantity = Decimal(product[4])
            total_price = Decimal(product[5])
            tax_percent = Decimal('10.0')  # or fetch dynamically

            discount_amount = (discount_percent / Decimal('100')) * unit_price * quantity
            taxable_amount = (unit_price * quantity) - discount_amount
            tax_amount = (tax_percent / Decimal('100')) * taxable_amount
                        # Now insert the row
            cursor.execute('''
                INSERT INTO sales_data (
                    bill_no, product_id, product_name, quantity, unit_price,
                    discount_percent, discount_amount,
                    tax_percent, tax_amount, total_price,
                    customer_name, contact, payment_mode, emp_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                invoice, product_id, product_name, quantity, unit_price,
                discount_percent, discount_amount,
                tax_percent, tax_amount, total_price,
                customer_name, contact, payment_mode, emp_name
            ))

        connection.commit()
        connection.close()
    except Exception as e:
        connection.rollback()
        connection.close()
        messagebox.showerror("Error", f"Failed to save sales data: {str(e)}")


def sales_form(dashboard):
    sales_dashboard = Frame(dashboard, bg='#D6E6EA')
    sales_dashboard.place(x=300, y=100, width=1230, relheight=1)
    sales_heading_label = Label(sales_dashboard, text='BILLING AREA', font=('Times New Roman', 20, 'bold'),
                                bg='#2B707F', fg='white')
    sales_heading_label.place(x=0, y=0, relwidth=1)
    prev_button = Button(sales_dashboard, text='Go Back', font=('Courier New', 10, 'italic'), fg='#002A37',
                         bg='#D6E6EA', bd=0, command=lambda: sales_dashboard.place_forget())
    prev_button.place(x=0, y=38)

    view_frame = Frame(sales_dashboard, bg="white", bd=2, relief=RIDGE)
    view_frame.place(x=10, y=80, width=1200, height=540)

    Label(view_frame, text="View Customer Bills", font=("goudy old style", 18),
          bg="#033054", fg="white", anchor="w", padx=10).pack(fill=X)

    # Center the invoice entry and buttons
    invoice_var = StringVar()
    Label(view_frame, text="Invoice No.", font=("times new roman", 14), bg="white").place(x=430, y=50)
    invoice_entry = Entry(view_frame, textvariable=invoice_var, font=("times new roman", 14), bg="lightyellow")
    invoice_entry.place(x=540, y=50, width=200, height=25)

    Button(view_frame, text="Search", command=lambda: search_bill(update_list=True),
           font=("times new roman", 12, "bold"), bg="#4caf50", fg="white", cursor="hand2").place(x=750, y=50, width=80, height=25)

    Button(view_frame, text="Clear", command=lambda: clear_bill_area(clear_list=True),
           font=("times new roman", 12, "bold"), bg="#616161", fg="white", cursor="hand2").place(x=840, y=50, width=80, height=25)

    # Bill Listbox
    bill_listbox = Listbox(view_frame, font=("times new roman", 13), bg="white")
    bill_listbox.place(x=10, y=100, width=300, height=400)
    bill_listbox.bind('<<ListboxSelect>>', lambda event: show_selected_bill())

    # Bill Area
    Label(view_frame, text="Customer Bill Area", font=("times new roman", 15),
          bg="orange", fg="black").place(x=320, y=80, width=860)
    bill_area = Text(view_frame, font=("times new roman", 12), bg="lightyellow")
    bill_area.place(x=320, y=110, width=860, height=390)

    # --- Functional Logic ---
    def search_bill(update_list=False):
        invoice = invoice_var.get().strip()
        found = False

        # Clear previous search results
        bill_area.delete("1.0", END)
        if update_list:
            bill_listbox.delete(0, END)

        for file in os.listdir("bill_data"):
            if file.startswith(invoice) and file.endswith(".txt"):
                if update_list:
                    bill_listbox.insert(END, file)
                else:
                    with open(f"bill_data/{file}", "r") as f:
                        bill_area.insert("1.0", f.read())
                    found = True
                    break

        if not found and not update_list:
            messagebox.showerror("Error", f"No invoice starting with '{invoice}' found.")

    def clear_bill_area(clear_list=False):
        invoice_var.set("")
        bill_area.delete("1.0", END)
        if clear_list:
            load_bills()

    def show_selected_bill():
        try:
            filename = bill_listbox.get(bill_listbox.curselection())
            with open(f"bill_data/{filename}", "r") as file:
                bill_area.delete("1.0", END)
                bill_area.insert("1.0", file.read())
        except:
            pass

    def load_bills():
        bill_listbox.delete(0, END)
        if not os.path.exists("bill_data"):
            os.makedirs("bill_data")
        for file in os.listdir("bill_data"):
            if file.endswith(".txt"):
                bill_listbox.insert(END, file)

    load_bills()
    dashboard.focus_force()
