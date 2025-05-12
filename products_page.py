from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
from firebase_config import *

def update_product(name, category, supplier, price, quantity, status, search_preview):
    cursor, connection = connect_database()
    
    selected = search_preview.selection()
    if not selected:
        messagebox.showerror('Error', 'Select a product to update')
        return

    content = search_preview.item(selected[0])
    values = content['values']
    product_id = values[0]

    if not cursor or not connection:
        return

    try:
        # Convert quantity to int and price to float
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror('Error', 'Price must be a number and quantity must be an integer')
        return

    cursor.execute('USE inventory_dbms')
    cursor.execute('SELECT * from product_details WHERE product_id=%s', (product_id,))
    currData = cursor.fetchone()

    if not currData:
        messagebox.showerror('Error', 'Product not found in database')
        return

    currData = currData[1:]  # Skip product_id
    new = (name, category, supplier, price, quantity, status)

    if currData == new:
        messagebox.showerror('Error', 'No changes made')
        return

    try:
        cursor.execute('''
            UPDATE product_details 
            SET product_name=%s, category=%s, supplier=%s, price=%s, quantity=%s, status=%s
            WHERE product_id=%s
        ''', (name, category, supplier, price, quantity, status, product_id))
        
        connection.commit()
        messagebox.showinfo('Success', 'Product updated successfully')
        preview_data(search_preview)
    except Exception as e:
        messagebox.showerror('Error', f'{e}')
    finally:
        cursor.close()
        connection.close()

def delete_product(treeview,name_entry,category_entry,supplier_entry,price_entry,quantity_entry,status_entry):
    sel = treeview.selection()
    
    if not sel:
        messagebox.showerror('Error', 'Nothing to delete! Kindly select a row.')
        return

    # Confirmation prompt
    confirm = messagebox.askyesno('Confirm Delete', 'Do you really want the product to be deleted?')
    if not confirm:
        return

    try:
        content = treeview.item(sel[0])
        values = content['values']
        id = values[0]

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        cursor.execute('USE inventory_dbms')
        cursor.execute('DELETE FROM product_details WHERE product_id=%s', (id,))
        connection.commit()
        messagebox.showinfo('Done', 'Record has been successfully deleted!')

        # Refresh Treeview after deletion
        preview_data(treeview)
        clear_function(name_entry,category_entry,supplier_entry,price_entry,quantity_entry,status_entry,True)
    except Exception as e:
        messagebox.showerror('Error', f'{e}')
    finally:
        if cursor: cursor.close()
        if connection: connection.close()



def select_product(event, search_preview, name_entry, category_entry, supplier_entry, price_entry, quantity_entry, status_entry):
    selected = search_preview.focus()  # This is more reliable than selection()[0]
    if not selected:
        return
    values = search_preview.item(selected, 'values')

    # Clear the entries first
    name_entry.delete(0, 'end')
    category_entry.set('Category')
    supplier_entry.set('Supplier Name')
    price_entry.delete(0, 'end')
    quantity_entry.delete(0, 'end')
    status_entry.set('Active')

    # Insert new values
    if values:
        name_entry.insert(0, values[1])
        category_entry.set(values[2])
        supplier_entry.set(values[3])
        price_entry.insert(0, values[4])
        quantity_entry.insert(0, values[5])
        status_entry.set(values[6])
        return

def clear_function(name,category,supplier,price,quantity,status,clear):
    name.delete(0,END)
    category.set('Category')
    supplier.set('Supplier Name')
    price.delete(0,END)
    quantity.delete(0,END)
    status.set('Active')
    
    if clear:
        search_preview.selection_remove(search_preview.selection())


def preview_data(search_preview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_dbms')
    try:
        cursor.execute('SELECT * FROM product_details')
        emp_records=cursor.fetchall()
        search_preview.delete(*search_preview.get_children())
        for r in emp_records:
            search_preview.insert('',END,values=r)
    except Exception as e:
        messagebox.showerror('Error',f'{e}')
    finally:
        cursor.close()
        connection.close()

def fetch_supp_cat(category_entry,supplier_entry):
    cursor,connection=connect_database()
    category_list=[]
    supplier_list=[]
    if not cursor or not connection:
        return 
    cursor.execute('USE inventory_dbms')
    cursor.execute('SELECT category_name FROM category_details')
    categories=cursor.fetchall()
    if len(categories)>0:
        for category in categories:
            category_list.append(category)
        category_entry.config(values=category_list)
    else: category_entry.set('Empty')

    cursor.execute('SELECT suppName FROM supplier_details')
    suppliers=cursor.fetchall()
    if len(suppliers)>0:
        for supplier in suppliers:
            supplier_list.append(supplier)
        supplier_entry.config(values=supplier_list)
    else: supplier_entry.set('Empty')





def add_product(name,category,supplier,price,quantity,status,treeview):
    if not all([name,price,quantity,status]):
        messagebox.showerror('Error', 'Please fill all the fields')
    elif category=='Empty':
        messagebox.showerror('Error','Please add categories')
    elif category=='Category':
        messagebox.showerror('Error','Please select category')
    elif supplier=='Empty':
        messagebox.showerror('Error','Please add suppliers')
    elif supplier=='Supplier Name':
        messagebox.showerror('Error','Please select supplier')
    else:
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror('Error', 'Price must be a number and Quantity must be an integer')
            return
        cursor,connection=connect_database()
        if not cursor or not connection:
            return
        cursor.execute('USE inventory_dbms')
        cursor.execute('SELECT * FROM product_details WHERE category=%s AND supplier=%s AND product_name=%s',(category,supplier,name))
        input_product=cursor.fetchone()
        if input_product:
            messagebox.showerror('Error','Product already exists')
            return
        cursor.execute('''INSERT INTO product_details(product_name, category, supplier, price, quantity, status)VALUES (%s, %s, %s, %s, %s, %s)''', (name, category, supplier, price, quantity, status))
        connection.commit()
        add_product_to_firestore(name, category, supplier, price, quantity, status)
        messagebox.showinfo('Success','Product added successfully')
        preview_data(treeview)

def search(search_combo, search_entry, treeview):
    filter_map = {
        'Product Name': 'product_name',
        'Category': 'category',
        'Supplier': 'supplier',
        'Status': 'status'
    }

    selected_filter = search_combo.get()
    search_value = search_entry.get()

    if selected_filter == 'Search Product By':
        messagebox.showerror('Error', 'Please select a search filter')
        return

    if search_value.strip() == '':
        messagebox.showerror('Error', 'Please enter the search value to search')
        return

    search_field = filter_map.get(selected_filter)
    if not search_field:
        messagebox.showerror('Error', 'Invalid search filter selected')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_dbms')
        # Using LIKE for partial matching (case-insensitive if DB collation allows)
        query = f"SELECT * FROM product_details WHERE {search_field} LIKE %s"
        cursor.execute(query, (f"%{search_value}%",))
        results = cursor.fetchall()

        treeview.delete(*treeview.get_children())  # Clear treeview

        if not results:
            messagebox.showinfo('Info', 'No matching products found')
            return

        for row in results:
            treeview.insert('', 'end', values=row)

    except Exception as e:
        messagebox.showerror('Error', f'{e}')
    finally:
        if cursor: cursor.close()
        if connection: connection.close()


def product_form(dashboard):
    global search_preview,category_entry,supplier_entry,name_entry,price_entry,quantity_entry,status_entry
    product_dashboard=Frame(dashboard,bg='#D6E6EA')
    product_dashboard.place(x=300,y=100,width=1230, relheight=1)
    product_heading_label=Label(product_dashboard,text='PRODUCT DETAILS',font=('Times New Roman',20,'bold'),bg='#2B707F',fg='white')
    product_heading_label.place(x=0,y=0,relwidth=1)
    prev_button=Button(product_dashboard,text='Go Back',font=('Courier New',10,'italic'),fg='#002A37',bg='#D6E6EA',bd=0,command=lambda: product_dashboard.place_forget())
    prev_button.place(x=0,y=38)


    left_frame=Frame(product_dashboard,bg='#D6E6EA',bd=3)
    left_frame.place(x=0,y=70,relwidth=0.5,relheight=1)
    right_frame=Frame(product_dashboard,bg='#D6E6EA')
    right_frame.place(relx=0.5,y=70,relwidth=0.5,relheight=0.8)

    manage_label=Label(left_frame,bg='black',fg='white',text='Manage Product Details',font=12)
    manage_label.place(x=0,y=5,relwidth=1)

    category_label = Label(left_frame, text='Category', font=12)
    category_label.grid(row=1, column=0, padx=20, pady=(60, 10), sticky='w')  # ⬅⬅⬅ Increased top padding only
    category_entry = ttk.Combobox(left_frame, state='readonly')
    category_entry.grid(row=1, column=1, pady=(60, 10))
    category_entry.set('Category')

    supplier_label = Label(left_frame, text='Supplier', font=12)
    supplier_label.grid(row=2, column=0, padx=20, pady=10, sticky='w')
    supplier_entry = ttk.Combobox(left_frame, state='readonly')
    supplier_entry.grid(row=2, column=1, pady=10)
    supplier_entry.set('Supplier Name')

    name_label = Label(left_frame, text='Name', font=12)
    name_label.grid(row=3, column=0, padx=20, pady=10, sticky='w')
    name_entry = Entry(left_frame)
    name_entry.grid(row=3, column=1, pady=20)

    price_label = Label(left_frame, text='Price', font=12)
    price_label.grid(row=4, column=0, padx=20, pady=10, sticky='w')
    price_entry = Entry(left_frame)
    price_entry.grid(row=4, column=1, pady=20)

    quantity_label = Label(left_frame, text='Quantity', font=12)
    quantity_label.grid(row=5, column=0, padx=20, pady=10, sticky='w')
    quantity_entry = Entry(left_frame)
    quantity_entry.grid(row=5, column=1, pady=20)

    status_label = Label(left_frame, text='Status', font=12)
    status_label.grid(row=6, column=0, padx=20, pady=10, sticky='w')
    status_entry = ttk.Combobox(left_frame,values=('Active','Inactive','Available','Not Available') ,state='readonly')
    status_entry.grid(row=6, column=1, pady=20)
    status_entry.set('Active')

    update_qty_label = Label(left_frame, text='Update Quantity By', font=12)
    update_qty_label.grid(row=7, column=0, padx=20, pady=(10, 5), sticky='w')

    update_qty_entry = Entry(left_frame)
    update_qty_entry.grid(row=7, column=1, pady=(10, 5))

    update_option = ttk.Combobox(left_frame, values=('Set','Add', 'Subtract'), state='readonly')
    update_option.grid(row=7, column=1, pady=5)
    update_option.set('Set')  # default

    def update_quantity():
        try:
            current_qty = int(quantity_entry.get())
            change = int(update_qty_entry.get())
            operation = update_option.get()

            if operation == 'Add':
                new_qty = current_qty + change
            elif operation == 'Subtract':
                new_qty = current_qty - change
                if new_qty < 0:
                    messagebox.showerror("Error", "Quantity cannot be negative")
                    return

            quantity_entry.delete(0, 'end')
            quantity_entry.insert(0, str(new_qty))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    button_frame=Frame(left_frame)
    button_frame.grid(row=9,columnspan=2,pady=10)

    add_button=Button(button_frame,text='Add',width=8,bg='#2B7075',fg='white',command=lambda:add_product(name_entry.get(),category_entry.get(),supplier_entry.get(),price_entry.get(),quantity_entry.get(),status_entry.get(),search_preview))
    add_button.grid(row=0,column=0,padx=10,pady=10)

    update_button=Button(button_frame,text='Update',width=8,bg='#2B7075',fg='white',command=lambda:update_product(name_entry.get(),category_entry.get(),supplier_entry.get(),price_entry.get(),quantity_entry.get(),status_entry.get(),search_preview))
    update_button.grid(row=0,column=1,padx=10,pady=10)

    delete_button=Button(button_frame,text='Delete',width=8,bg='#2B7075',fg='white',command=lambda: delete_product(search_preview,name_entry,category_entry,supplier_entry,price_entry,quantity_entry,status_entry))
    delete_button.grid(row=0,column=2,padx=10,pady=10)

    clear_button=Button(button_frame,text='Clear',width=8,bg='#2B7075',fg='white',command=lambda: clear_function(name_entry,category_entry,supplier_entry,price_entry,quantity_entry,status_entry,True))
    clear_button.grid(row=0,column=3,padx=10,pady=10)

    search_frame = LabelFrame(right_frame, text='Search Product', fg='black', font=('Arial', 12, 'bold'), bg='#D6E6EA', bd=2)
    search_frame.place(x=10, y=5, relwidth=0.95, height=100)

    search_combo=ttk.Combobox(search_frame,values=('Category','Product Name','Supplier Name','Status'),state='readonly',width=16)
    search_combo.set('Search Product By')
    search_combo.grid(row=0,column=0,padx=10,pady=10)

    search_entry=Entry(search_frame,width=16)
    search_entry.grid(row=0,column=1,padx=10)

    search_button=Button(search_frame,text='Search',font=3,width=8,bg='#2B7075',fg='white',command=lambda: search(search_combo,search_entry,search_preview))
    search_button.grid(row=0,column=2,padx=10)

    showAll_button=Button(search_frame,text='Show All',font=3,width=8,bg='#2B7075',fg='white',command=lambda: preview_data(search_preview))
    showAll_button.grid(row=0,column=3,padx=10)

    search_preview_frame=Frame(right_frame,bg='white')
    search_preview_frame.place(x=10,y=105,relwidth=0.95,relheight=0.8)
    horizontal_sb=Scrollbar(search_preview_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(search_preview_frame,orient=VERTICAL)
    search_preview = ttk.Treeview(search_preview_frame, show='headings',columns=('id','name','category','supplier','price','quantity','status'),yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    horizontal_sb.pack(side=BOTTOM,fill=X)
    vertical_sb.pack(side=RIGHT,fill=Y)
    search_preview.pack()
    horizontal_sb.config(command=search_preview.xview)
    vertical_sb.config(command=search_preview.yview)

    search_preview.heading('id',text='Product Id')
    search_preview.heading('category',text='Category')
    search_preview.heading('supplier',text='Supplier Name')
    search_preview.heading('name',text='Product Name')
    search_preview.heading('price',text='Price')
    search_preview.heading('quantity',text='Quantity')
    search_preview.heading('status',text='Status')

    search_preview.column('id',width=70)
    search_preview.column('category',width=100)
    search_preview.column('supplier',width=100)
    search_preview.column('name',width=100)
    search_preview.column('price',width=70)
    search_preview.column('quantity',width=100)
    search_preview.column('status',width=100)


    fetch_supp_cat(category_entry,supplier_entry)
    preview_data(search_preview)

    search_preview.bind('<ButtonRelease-1>',lambda event: select_product(event,search_preview,name_entry,category_entry,supplier_entry,price_entry,quantity_entry,status_entry))


    return product_dashboard

