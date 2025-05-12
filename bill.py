from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
import time
import os
import tempfile
from sales import save_sales_to_db


def clear_cart(product_name_entry, price_entry, stock_label, customer_name_entry, customer_contact_entry,cart_list,cart_list_clear,cart_preview):
    # Make entries editable before clearing
    if cart_list_clear==0:
        product_name_entry.config(state='normal')
        price_entry.config(state='normal')
        customer_name_entry.config(state='normal')
        customer_contact_entry.config(state='normal')

        # Clear entries
        price_entry.delete(0, END)
        customer_name_entry.delete(0, END)
        product_name_entry.delete(0, END)
        customer_contact_entry.delete(0, END)

        # Reset back to readonly if needed
        product_name_entry.config(state='readonly')
        price_entry.config(state='readonly')

        # Update stock label
        stock_label.config(text='In Stock []')
    else:
        cart_list.clear()
        print('Cart list checking',cart_list)
        for item in cart_preview.get_children():
            cart_preview.delete(item)

def show_cart_menu(event, menu):
    selected_item = event.widget.identify_row(event.y)
    if selected_item:
        event.widget.selection_set(selected_item)
        menu.post(event.x_root, event.y_root)

def delete_cart_item(cart_preview, cart_list, lbl_amnt):
    selected_item = cart_preview.focus()
    if not selected_item:
        return
    values = cart_preview.item(selected_item, 'values')
    pd_id = values[0]

    response = messagebox.askyesno('Confirm Delete', f'Do you want to delete {values[1]} from the cart?')
    if response:
        for i, item in enumerate(cart_list):
            if item[0] == pd_id:
                cart_list.pop(i)
                break
        # Refresh Treeview
        cart_preview.delete(*cart_preview.get_children())
        for item in cart_list:
            cart_preview.insert('', 'end', values=item)
        total_bill(cart_list, lbl_amnt)

def generate_bill(customer_name_entry, contact_entry, bill_text, cart_list,
                  product_preview, price_entry, stock_label, event):
    if customer_name_entry.get() == '' or contact_entry.get() == '':
        messagebox.showerror('Error', 'Please fill in the customer details!')
    elif len(cart_list) == 0:
        messagebox.showerror('Error', 'No items in the cart!')
    else:
        invoice = bill_top(customer_name_entry, contact_entry, bill_text)
        bill_center(cart_list, bill_text, event, product_preview, customer_name_entry, price_entry, stock_label)

        # Call total_bill and use its returned values
        bill_amount, tax_percent, net_amount = total_bill(cart_list, lbl_amount=None, lbl_tax=None, lbl_total=None)
        tax_amount = (tax_percent / 100) * bill_amount

        bill_bottom(bill_amount, tax_amount, net_amount, bill_text)

        if not os.path.exists('bill_data'):
            os.makedirs('bill_data')

        with open(f'bill_data/{str(invoice)}.txt', 'w') as file:
            file.write(bill_text.get('1.0', END))

        messagebox.showinfo('Success', 'Bill is generated successfully!')

        # Save to database
        save_sales_to_db(cart_list, invoice, customer_name_entry.get(), contact_entry.get())

        

def bill_top(name_entry, contact_entry, bill_text):
    time_part = int(time.strftime("%H%M%S"))     # e.g., 145320
    date_part = int(time.strftime("%d%m%Y"))     # e.g., 15042025
    invoice = f"{time_part}{date_part}"          # Combine into string for display and file naming

    billTop_template = f'''\t\t   INVENTORY MANAGEMENT
 Contact: +92 340 6523963 \t\t\t\t\tKhi, Pakistan.
    \t\t ==============================
 BILL NO: {invoice}\t\t\t\t\tDATE: {date.today()}
 CUSTOMER NAME: {name_entry.get()}\t\t\t\t\tTIME: {time.strftime("%H:%M:%S")}
 CONTACT NO: {contact_entry.get()}
    \t\t-----------------------------
 Product Name\t Qty\t\tPrice\t Discount\t  Total
    \t\t-----------------------------'''

    bill_text.delete(1.0, 'end')
    bill_text.insert('1.0', billTop_template)
    
    return invoice  # still returns string for filename usage


def bill_center(cart_list, bill_text, event, product_preview, name_entry, price_entry, stock_label):
    cursor, connection = connect_database()
    try:
        for product in cart_list:
            name = product[1]
            price = float(product[2])
            discount_percent = float(product[3]) if product[3] else 0
            qty = int(product[4])
            total = float(product[5])

            # Get product details from DB
            values = select_product(event, product_preview, name_entry, price_entry, stock_label)
            pid = values[0]
            current_stock = int(values[3])

            new_stock = current_stock - qty
            status = 'Inactive' if new_stock == 0 else 'Active'

            cursor.execute(
                'UPDATE product_details SET quantity=%s, status=%s WHERE product_id=%s',
                (new_stock, status, pid)
            )

            discount_amount = (discount_percent / 100) * price * qty

            # Format product line
            line = f"\n {name}\t\t{qty}\t {price:.2f}\t  {discount_amount:.2f}\t   {total:.2f}"
            bill_text.insert(END, line)

        connection.commit()
        connection.close()
        preview_product(product_preview, '', False)

    except Exception as e:
        print("Error in bill_center:", str(e))
        connection.rollback()
        connection.close()
        messagebox.showerror('Error', f"An error occurred while generating bill center: {str(e)}")


def bill_bottom(total_bill_amount, tax_amount, final_amount, bill_text):
    billBottom_template = f'''
\t\t-----------------------------
 Bill Amount   : PKR {total_bill_amount:.2f}
 Tax Amount    : PKR {tax_amount:.2f}
 Total Payable : PKR {final_amount:.2f}
\t\t-----------------------------'''
    bill_text.insert(END, billBottom_template)


# --- TOTAL BILL CALCULATION FUNCTION ---

def total_bill(cart_list, lbl_amount=None, lbl_tax=None, lbl_total=None):
    global net_pay
    bill_amount = sum(row[5] for row in cart_list)  # Sum of total prices (discount already applied)

    cursor, connection = connect_database()
    if not cursor or not connection:
        return 0, 0, 0
    else:
        cursor.execute('USE inventory_dbms')
        cursor.execute('SELECT * FROM tax_data')
        tax = cursor.fetchone()
        if tax:
            tax = float(tax[1]) / 100
        else:
            tax = 0

        tax_amount = bill_amount * tax
        net_pay = bill_amount + tax_amount

        # Update labels if provided
        if lbl_amount and lbl_tax and lbl_total:
            lbl_amount.config(text="Bill Amount\n $%.2f" % bill_amount)
            lbl_tax.config(text="Tax\n %.2f%%" % (tax * 100))
            lbl_total.config(text="Total\n $%.2f" % net_pay)

        return round(bill_amount, 2), round(tax * 100, 2), round(net_pay, 2)

def add_cart(qty, price, product_preview, name_entry, stock_label, discount, cart_list, cart_preview, lbl_amnt,lbl_tax,lbl_total):
    try:
        if qty.get() == '':
            messagebox.showerror("Error", "Quantity cannot be empty")
            return
        elif not qty.get().isdigit():
            messagebox.showerror("Error", "Quantity must be a valid positive integer or zero")
            return
        elif price.get() == '':
            messagebox.showerror("Error", "Please select a product")
            return

        qty_val = int(qty.get())
        price_val = float(price.get())
        discount_val = float(discount.get()) if discount.get().strip() != '' else 0
        discount_display = discount.get().strip() if discount.get().strip() != '' else '0'
        total_price = price_val * qty_val * (1 - discount_val / 100)

        values = select_product(None, product_preview, name_entry, price, stock_label)
        if not values:
            return
        pd_id = values[0]

        # Check if product already in cart
        present = False
        index = 0
        for i, item in enumerate(cart_list):
            if item[0] == pd_id:
                present = True
                index = i
                break
        stock_available = int(values[3])  # Stock from selected product

        if present:
            if qty_val == 0:
                response = messagebox.askyesno('Confirm Delete', 'Quantity is 0.\nDo you want to remove this item from the cart?')
                if response:
                    cart_list.pop(index)
            else:
                if qty_val > stock_available:
                    messagebox.showerror('Error', f'Only {stock_available} items in stock')
                    return
                response = messagebox.askyesno('Confirm Update', f"Updating the quantity of {name_entry.get()} to {qty_val}.\nDo you want to proceed?")
                if response:
                    cart_list[index][5] = total_price
                    cart_list[index][4] = str(qty_val)
                    cart_list[index][3] = discount_display
        else:
            if qty_val > stock_available:
                messagebox.showerror('Error', f'Only {stock_available} items in stock')
                return
            if qty_val > 0:
                cart_data = [pd_id, name_entry.get(), price.get(), discount_display, qty.get(), total_price]
                cart_list.append(cart_data)


        # Clear and repopulate Treeview
        cart_preview.delete(*cart_preview.get_children())
        for item in cart_list:
            cart_preview.insert('', 'end', values=item)

        # Clear fields
        qty.delete(0, END)
        qty.insert(0, '1')

        discount.delete(0, END)
        discount.insert(0, '0')
        
        total_bill(cart_list, lbl_amnt,lbl_tax,lbl_total)
        
    except Exception as e:
        messagebox.showerror('Error', f'{e}')

def select_product(event, product_preview, name_entry, price_entry, stock_label):
    selected = product_preview.focus()
    if not selected:
        return
    values = product_preview.item(selected, 'values')

    if values:
        name_entry.config(state='normal')
        price_entry.config(state='normal')

        name_entry.delete(0, END)
        price_entry.delete(0, END)

        name_entry.insert(0, values[1])
        price_entry.insert(0, values[2])

        name_entry.config(state='readonly')
        price_entry.config(state='readonly')
        stock_label.config(text=f'In Stock [{values[3]}]')

        return values

def get_selected_product_values(product_preview):
    selected = product_preview.focus()
    if not selected:
        return None
    values = product_preview.item(selected, 'values')
    return values


def search_by_name(search_entry, treeview):
    search_value = search_entry.get().strip()

    if not search_value:
        messagebox.showerror('Error', 'Please enter a product name to search')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_dbms')

        # Search by product name only (partial match using LIKE)
        query = "SELECT product_id, product_name, price, quantity, status FROM product_details WHERE product_name LIKE %s"
        cursor.execute(query, (f"%{search_value}%",))
        results = cursor.fetchall()

        # Clear treeview before inserting new results
        treeview.delete(*treeview.get_children())

        if not results:
            messagebox.showinfo('Info', 'No matching products found')
            return

        for row in results:
            treeview.insert('', 'end', values=row)

    except Exception as e:
        messagebox.showerror('Error', f'Error while searching: {e}')
    finally:
        cursor.close()
        connection.close()


def preview_product(product_preview,search_entry,show):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_dbms')
    try:
        
        cursor.execute('SELECT product_id,product_name,price,quantity,status FROM product_details where status="Active" or status="Available"')
        emp_records=cursor.fetchall()
        product_preview.delete(*product_preview.get_children())
        for r in emp_records:
            product_preview.insert('',END,values=r)
        if show==True:
            search_entry.delete(0,END)
    except Exception as e:
        messagebox.showerror('Error',f'{e}')
    finally:
        cursor.close()
        connection.close()
def logout(current_window):
    response=messagebox.askyesno('LOG OUT','Are You sure you wat to logout of the current account?')
    if response:
        current_window.destroy()  # Close the dashboard window
        from login import login_window  # Import the login window from the login module
        login_window()  # Open the login window

    

def bill_form():
    dashboard=Tk()

    dashboard.title('INVENTORY MANAGEMENT SYSTEM')
    dashboard.geometry('1520x715+0+0')
    dashboard.configure(bg='#f0f0f0')
    #dashboard.resizable(0,0)
    #creating label
    logo=PhotoImage(file='C:/Users/PC/Downloads/icons8-inventory-64.png')
    logo.zoom(10)
    titlelabel=Label(dashboard,image=logo,compound=LEFT,padx=20,text='INVENTORY MANAGEMENT SYSTEM',font=('Helvetica',20),bg='#00404E',fg='white')
    #placing label
    titlelabel.pack()
    titlelabel.place(relwidth=1)

    welcome_label=Label(dashboard,text='Welcome',font=20,bg='#DADADA')
    welcome_label.place(x=0,y=70, relwidth=1)


    bill_dashboard=Frame(dashboard,bg='#D6E6EA')
    bill_dashboard.place(x=0,y=100,relwidth=1, relheight=1)
    bill_heading_label=Label(bill_dashboard,text='BILLING AREA',font=('Times New Roman',20,'bold'),bg='#2B707F',fg='white')
    bill_heading_label.place(x=0,y=0,relwidth=1)

    logout_btn = Button(bill_heading_label, text="Logout", font=('Arial', 12), bg='#2B707F', fg='white',command=lambda: logout(dashboard))  # Make sure you define a logout() function
    logout_btn.pack(side='right', padx=10, pady=5)

    product_frame=Frame(bill_dashboard,bg='yellow',bd=2)
    product_frame.place(x=3,y=50,relwidth=0.33,relheight=0.80)

    # Configure 2 columns (for label-entry and buttons)
    product_frame.columnconfigure(0, weight=1)
    product_frame.columnconfigure(1, weight=1)

# Title Label
    product_label = Label(product_frame, bg='black', fg='white', text='Product Details', font=12)
    product_label.grid(row=0, column=0, columnspan=2, sticky='ew')

# Row 1: Label and Entry
    Label(product_frame, text='Search Product By Name', font=12).grid(row=1, column=0, padx=10, pady=(10,5), sticky='e')

    product_name_entry = Entry(product_frame, font=('Arial', 10))
    product_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

# Row 2: Buttons (Search and Show All)
    show_all_button = Button(product_frame, text='Show All', font=('Arial', 10, 'bold'), bg='#2B7075', fg='white',command=lambda:preview_product(product_preview,product_name_entry,True))
    show_all_button.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

    search_button = Button(product_frame, text='Search', font=('Arial', 10, 'bold'), bg='#2B7075', fg='white',command=lambda: search_by_name(product_name_entry, product_preview))
    search_button.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

    preview_frame=Frame(product_frame,bg='#DADADA')
    preview_frame.place(x=0,y=120,relwidth=1,relheight=0.75)
    horizontal_sb=Scrollbar(preview_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(preview_frame,orient=VERTICAL)
    product_preview = ttk.Treeview(preview_frame, show='headings',yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    horizontal_sb.pack(side=BOTTOM,fill=X)
    vertical_sb.pack(side=RIGHT,fill=Y)
    product_preview.pack()
    horizontal_sb.config(command=product_preview.xview)
    vertical_sb.config(command=product_preview.yview)

    columns=('id','name','price','quantity','status')
    product_preview['columns'] = columns

    product_preview.heading('id',text='Id')
    product_preview.heading('name',text='Name')
    product_preview.heading('price',text='Price')
    product_preview.heading('quantity',text='Quanity')
    product_preview.heading('status',text='Status')

    product_preview.column('id', width=40, anchor='center')
    product_preview.column('name', width=150, anchor='w')
    product_preview.column('price', width=99, anchor='center')
    product_preview.column('quantity', width=90, anchor='center')
    product_preview.column('status', width=100, anchor='center')

    customer_frame=Frame(bill_dashboard,bg='red',bd=2)
    customer_frame.place(relx=0.33,y=50,relwidth=0.33,relheight=0.80)

    customer_label=Label(customer_frame, bg='black', fg='white', text='Customer Details', font=12)
    customer_label.place(x=0, y=0, relwidth=1)

    customer_frame1=Frame(customer_frame, bg='white')
    customer_frame1.place(x=0, y=30, relwidth=1, height=50)
    cust_name_label=Label(customer_frame1,text='Customer Name')
    cust_name_label.grid(row=0,column=0,padx=10,pady=10)
    name_entry=Entry(customer_frame1)
    name_entry.grid(row=0,column=1,padx=10,pady=10)
    cust_cont_label=Label(customer_frame1,text='Contact')
    cust_cont_label.grid(row=0,column=2,padx=10,pady=10)
    contact_entry=Entry(customer_frame1)
    contact_entry.grid(row=0,column=3,padx=10,pady=10)

    customer_frame2=Frame(customer_frame,bg='yellow')
    customer_frame2.place(x=0, y=90, relwidth=1, relheight=0.7)
    
    cart_frame=Frame(customer_frame2)
    cart_frame.place(relx=0.5,y=0,relwidth=0.5,relheight=1)
    cart_list=[]
    cart_title=Label(cart_frame,text='Cart \t\t Total Product[0]',bg='white',fg='black')
    cart_title.place(x=0, y=0, relwidth=1)
    horizontal_sb=Scrollbar(cart_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(cart_frame,orient=VERTICAL)
    cart_preview = ttk.Treeview(cart_frame, show='headings',yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    cart_preview.place(x=0, y=30, relwidth=0.95, relheight=0.87)     # Leaves space for both scrollbars
    vertical_sb.place(relx=0.95, y=30, relheight=0.87, relwidth=0.05)
    horizontal_sb.place(x=0, rely=0.94, relwidth=0.95, height=15) 
    horizontal_sb.config(command=cart_preview.xview)
    vertical_sb.config(command=cart_preview.yview)

    columns=('id','name','price','discount','quantity','total price')
    cart_preview['columns'] = columns

    cart_preview.heading('id',text='Id')
    cart_preview.heading('name',text='Name')
    cart_preview.heading('price',text='Price')
    cart_preview.heading('discount',text='Discount')
    cart_preview.heading('quantity',text='Quanity')
    cart_preview.heading('total price',text='Total Price')

    cart_preview.column('id', width=40, anchor='center')
    cart_preview.column('name', width=150, anchor='w')
    cart_preview.column('price', width=99, anchor='center')
    cart_preview.column('discount', width=99, anchor='center')
    cart_preview.column('quantity', width=90, anchor='center')
    cart_preview.column('total price', width=99, anchor='center')

    customer_button_frame=Frame(customer_frame,bg='yellow')
    customer_button_frame.place(x=0,rely=0.85,relwidth=1,relheight=0.3)

    pd_name_label=Label(customer_button_frame,text='Product Name',)
    pd_name_label.grid(row=0,column=0,padx=2,pady=5)
    pd_name_entry=Entry(customer_button_frame,width=22,state='readonly')
    pd_name_entry.grid(row=1,column=0,padx=2)
    pd_price_label=Label(customer_button_frame,text='Price per unit')
    pd_price_label.grid(row=0,column=1,padx=2,pady=5)
    pd_price_entry=Entry(customer_button_frame,width=18,state='readonly')
    pd_price_entry.grid(row=1,column=1,padx=2)
    pd_discount_label=Label(customer_button_frame,text='Product Discount (%)')
    pd_discount_label.grid(row=0,column=2,padx=2,pady=5)
    pd_discount_entry=Entry(customer_button_frame,width=18)
    pd_discount_entry.grid(row=1,column=2,padx=2)
    pd_quantity_label=Label(customer_button_frame,text='Quantity')
    pd_quantity_label.grid(row=0,column=3,pady=5,padx=2)
    pd_quantity_entry=Entry(customer_button_frame,width=18)
    pd_quantity_entry.grid(row=1,column=3,padx=2)
    pd_quantity_entry.insert(0, '1')
    pd_stock_label=Label(customer_button_frame,text='In Stock [0]')
    pd_stock_label.grid(row=2,column=0,padx=2,pady=5)
    
    add_button = Button(customer_button_frame, bg='lightgray', fg='black', text='Add | Update Cart', width=20,command=lambda: add_cart(pd_quantity_entry, pd_price_entry, product_preview,pd_name_entry, pd_stock_label, pd_discount_entry, cart_list,cart_preview,lbl_amount,lbl_tax,lbl_total))
    add_button.grid(row=2, column=1, padx=2, pady=5)
    clear_button=Button(customer_button_frame,bg='lightgray',fg='black',text='Clear',width=16,command=lambda:clear_cart(product_name_entry, pd_price_entry, pd_stock_label, name_entry, contact_entry,cart_list,0,cart_preview))
    clear_button.grid(row=2,column=3,padx=2,pady=5)
                                                        
    clearCart_button=Button(customer_button_frame,bg='lightgray',fg='black',text='Clear Cart',width=16,command=lambda:clear_cart(product_name_entry, pd_price_entry, pd_stock_label, name_entry, contact_entry,cart_list,1,cart_preview))
    clearCart_button.grid(row=2,column=2,padx=2,pady=5)
# Calculator frame inside customer_frame2
    cal_frame = Frame(customer_frame2, bg='gray', bd=1)
    cal_frame.place(x=0, y=0, relwidth=0.5, relheight=1)

# Entry display
    cal_entry = Entry(cal_frame, bd=2, font=("Arial", 18), justify='right', bg='white', fg='black')
    cal_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=10, sticky='nsew')

# Button click handler
    def btn_click(char):
        cal_entry.insert(END, char)

    def calculate():
        try:
            result = str(eval(cal_entry.get()))
            cal_entry.delete(0, END)
            cal_entry.insert(END, result)
        except:
            cal_entry.delete(0, END)
            cal_entry.insert(END, "Error")

    def clear():
        cal_entry.delete(0, END)

# Buttons layout
    buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', 'C', '=', '+']]

# Button styles
    btn_bg = "lightgray"
    btn_fg = "black"
    btn_font = ("Arial", 14, "bold")

# Create buttons
    for r, row in enumerate(buttons):
        for c, char in enumerate(row):
            action = (
                calculate if char == '=' else
                clear if char == 'C' else
                lambda ch=char: btn_click(ch)
                      )
            btn = Button(
                cal_frame, text=char, width=5, height=2,
                bg=btn_bg, fg=btn_fg, font=btn_font,
                command=action)
            btn.grid(row=r+1, column=c, padx=4, pady=4, sticky='nsew')

# Make buttons expand with window
    for i in range(5):
        cal_frame.grid_rowconfigure(i, weight=1)
    for j in range(4):
        cal_frame.grid_columnconfigure(j, weight=1)





    account_frame=Frame(bill_dashboard,bg='green',bd=2)
    account_frame.place(relx=0.66,y=50,relwidth=0.333,relheight=0.80)

    bill_label=Label(account_frame,bg='black',fg='White',text='Customer Billing Area',font=12)
    bill_label.place(x=0,y=0,relwidth=1)

    bill_area=Frame(account_frame,bd=2,background='blue')
    bill_area.place(x=0,y=40,relwidth=1,height=440)

    
    vertical_sb=Scrollbar(bill_area,orient=VERTICAL)
    vertical_sb.pack(side=RIGHT,fill=Y)
    bill_text=Text(bill_area,yscrollcommand=vertical_sb.set)
    bill_text.pack(fill=BOTH,expand=1)
    vertical_sb.config(command=bill_text.yview)


    bill_button_frame = Frame(account_frame, bg='black', bd=2)
    bill_button_frame.place(x=0, y=490, relwidth=1, height=120)

# Configure 4 equal columns
    for i in range(4):
        bill_button_frame.grid_columnconfigure(i, weight=1)

# Configure two rows: one for labels, one for buttons
    bill_button_frame.grid_rowconfigure(0, weight=2)
    bill_button_frame.grid_rowconfigure(1, weight=1)

# Label styling
    label_font = ("Arial", 12, "bold")
    label_fg = "white"

# Row 0 - Info Labels
    lbl_amount = Label(bill_button_frame, text='Bill Amount\n[0]', bg='#209876', fg=label_fg, font=label_font, justify='center')
    lbl_amount.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

    lbl_discount = Label(bill_button_frame, text='Discount\n[5%]', bg='#345678', fg=label_fg, font=label_font, justify='center')
    lbl_discount.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

    lbl_tax = Label(bill_button_frame, text='Tax\n[0]', bg='#678910', fg=label_fg, font=label_font, justify='center')
    lbl_tax.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

    lbl_total = Label(bill_button_frame, text='Total\n[0]', bg='#345678', fg=label_fg, font=label_font, justify='center')
    lbl_total.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')

# Row 1 - 4 Buttons
    btn1 = Button(bill_button_frame, text="Generate/Save Bill", bg='green', fg='white',command=lambda:generate_bill(name_entry, contact_entry, bill_text, cart_list,product_preview,pd_price_entry,pd_stock_label,None))
    btn1.grid(row=1, column=0,columnspan=4, padx=5, pady=5, sticky='nsew')

    cart_menu = Menu(cart_preview, tearoff=0)
    cart_menu.add_command(label="Delete", command=lambda: delete_cart_item(cart_preview, cart_list, lbl_amount))

    
    preview_product(product_preview,product_name_entry,False)
    product_preview.bind('<ButtonRelease-1>', lambda event: select_product(event, product_preview, pd_name_entry, pd_price_entry, pd_stock_label))
    cart_preview.bind("<Button-3>", lambda event: show_cart_menu(event, cart_menu))


