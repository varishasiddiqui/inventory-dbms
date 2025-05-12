from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
from firebase_config import *

def insert_data():
    invoiceNo=invoice_entry.get()
    name=supplier_entry.get().lower()
    contact=contact_entry.get()
    email=email_entry.get()
    address=address_entry.get(1.0,END).lower()
    description=description_entry.get(1.0,END).lower()
    
    return invoiceNo,name,contact,email,address,description

def save_supplier():
    invoiceNo,name,contact,email,address,description=insert_data()
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    if not invoiceNo:
        cursor.execute("SELECT MAX(invoiceNo) FROM supplier_details")
        last_invoice = cursor.fetchone()[0]
        new_invoice = 1 if last_invoice is None else last_invoice + 1
        invoice_entry.insert(0, str(new_invoice))
        id=str(new_invoice)
    
    if not name:
        messagebox.showerror('Error', 'Please enter supplier name')
        return
    contact = contact if contact else None
    cursor.execute('USE inventory_dbms')
    try:

        cursor.execute('''INSERT INTO supplier_details(invoiceNo, suppName, suppContact, suppEmail,suppAddress,suppDes) VALUES (%s,%s,%s,%s,%s,%s)''',
        (invoiceNo,name,contact,email,address, description))
        connection.commit()
        add_supplier_to_firebase(invoiceNo,name,contact,email,address,description)
        messagebox.showinfo('Success', 'Supplier details saved successfully!')
        preview_supplier_data()
    except Exception as e:
        messagebox.showerror('Error', f'{e}')

def preview_supplier_data():
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_dbms')
    try:
        cursor.execute('SELECT * FROM supplier_details')
        emp_records=cursor.fetchall()
        supplier_search_preview.delete(*supplier_search_preview.get_children())
        for r in emp_records:
            supplier_search_preview.insert('',END,values=r)
    except Exception as e:
        messagebox.showerror('Error',f'{e}')
    finally:
        cursor.close()
        connection.close()

def clear_function(invoiceNo, suppName,suppContact,suppEmail,suppAddress,suppDes,clear):
    invoiceNo.delete(0,END)
    suppName.delete(0,END)
    suppContact.delete(0,END)
    suppEmail.delete(0,END)
    suppAddress.delete(1.0,END)
    suppDes.delete(1.0,END)
    
    if clear:
        supplier_search_preview.selection_remove(supplier_search_preview.selection())

def select_supplier(event,invoiceNo,suppName,suppContact,suppEmail,suppAddress,suppDes):
    index=supplier_search_preview.selection()
    content=supplier_search_preview.item(index)
    values=content['values']
    clear_function(invoiceNo,suppName,suppContact,suppEmail,suppAddress,suppDes,False)
    invoice_entry.insert(0,values[0])
    supplier_entry.insert(0,values[1])
    contact_entry.insert(0,values[2])
    email_entry.insert(0,values[3])
    address_entry.insert(INSERT,values[4])
    description_entry.insert(INSERT,values[5])

def update_supplier_func(invoiceNo, suppName, suppContact, suppEmail, suppAddress, suppDes):
    selected = supplier_search_preview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Supplier is selected!')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_dbms')
            cursor.execute('SELECT * FROM supplier_details WHERE invoiceNo=%s', (invoiceNo,))
            currData = cursor.fetchone()
            if currData:
                currData = currData[1:]
                new = (suppName, suppContact, suppEmail, suppAddress, suppDes)
                if currData == new:
                    messagebox.showinfo('Info: ', 'Nothing to Update!')
                else:
                    cursor.execute('''
                        UPDATE supplier_details SET
                        suppName=%s,
                        suppContact=%s,
                        suppEmail=%s,
                        suppAddress=%s,
                        suppDes=%s
                        WHERE invoiceNo=%s
                    ''', (suppName, suppContact, suppEmail, suppAddress, suppDes, invoiceNo))

                    if suppContact is None or suppContact == '':
                        suppContact = None  # Fixing the logic for assigning None to suppContact
                    
                    connection.commit()
                    # Refresh the Treeview after update
                    update_treeview_data()
                    messagebox.showinfo('UPDATED', f'Details updated for invoice: {invoiceNo}')
                    preview_supplier_data()
            else:
                messagebox.showerror('Error', 'Invoice number not found.')

        except Exception as e:
            messagebox.showerror('Error', f'{e}') 
        finally:
            cursor.close()
            connection.close()



def delete_function(invoice):
    sel=supplier_search_preview.selection()
    if not sel:
        messagebox.showerror('Error','Nothing to Delete! Kindly select a row.')
    else:
        if not invoice:
            messagebox.showerror('Error','Invoice No. field is empty!')
            return
        response=messagebox.askquestion('Attention',f'Do you really want to delete the record for Invoice No: {invoice}?')
        if response=='yes':
            cursor,connection=connect_database()
            if not cursor or not connection:
                return
            cursor.execute('use inventory_dbms')
            cursor.execute('DELETE FROM supplier_details where invoiceNo=%s',(invoice,))
            connection.commit()
            messagebox.showinfo('Done',f'Record for Invoice No. :{invoice} has been successfully deleted!')
            preview_supplier_data()

def search_function(invoice):
    if invoice=='':
        messagebox.showerror('Error','Enter data to search!')
    else:
        cursor,connection=connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_dbms')
            cursor.execute(f'SELECT * FROM supplier_details WHERE invoiceNo=%s',(invoice,))
            search=cursor.fetchall()
            supplier_search_preview.delete(*supplier_search_preview.get_children())
            for record in search:
                supplier_search_preview.insert('',END,value=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error: {e}')
        finally:
            cursor.close()
            connection.close()


def update_treeview_data():
    # Clear the Treeview before inserting new data
    for item in supplier_search_preview.get_children():
        supplier_search_preview.delete(item)

    # Fetch and populate the updated data
    cursor, connection = connect_database()
    if cursor and connection:
        try:
            cursor.execute('SELECT * FROM supplier_details')
            data = cursor.fetchall()
            for row in data:
                supplier_search_preview.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror('Error', f'{e}')
        finally:
            cursor.close()
            connection.close()

def count_supplier():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return 0
    try:
        cursor.execute('SELECT COUNT(invoiceNo) FROM supplier_details')
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        messagebox.showerror('Error', f'{e}')
        return 0
    finally:
        cursor.close()
        connection.close()


def supplier_form(dashboard):
    global supplier_entry,contact_entry, invoice_entry,email_entry,address_entry,description_entry,supplier_search_preview
    supplier_dashboard=Frame(dashboard,bg='#D6E6EA')
    supplier_dashboard.place(x=300,y=100,width=1230, relheight=1)
    supplier_heading_label=Label(supplier_dashboard,text='SUPPLIERS DETAILS',font=('Times New Roman',20,'bold'),bg='#2B707F',fg='white')
    supplier_heading_label.place(x=0,y=0,relwidth=1)
    prev_button=Button(supplier_dashboard,text='Go Back',font=('Courier New',10,'italic'),fg='#002A37',bg='#D6E6EA',bd=0,command=lambda: supplier_dashboard.place_forget())
    prev_button.place(x=0,y=38)
    
    invoice_frame=Frame(supplier_dashboard,bg='#D6E6EA')
    invoice_frame.place(x=30,y=150,width=550,relheight=1)
    
    
    invoice_label=Label(invoice_frame,text='Invoice No: ',font=13,bg='#D6E6EA')
    invoice_label.grid(row=0,column=0,padx=20)
    invoice_entry=Entry(invoice_frame)
    invoice_entry.grid(row=0,column=1,columnspan=2,padx=10,pady=10)
    
    supplier_label=Label(invoice_frame,text='Supplier Name: ',font=13,bg='#D6E6EA')
    supplier_label.grid(row=1,column=0,padx=20,pady=10)
    supplier_entry=Entry(invoice_frame)
    supplier_entry.grid(row=1,column=1,columnspan=2,padx=10,pady=10)
    
    contact_label=Label(invoice_frame,text='Contact: ',font=13,bg='#D6E6EA')
    contact_label.grid(row=2,column=0,padx=20,pady=10)
    contact_entry=Entry(invoice_frame)
    contact_entry.grid(row=2,column=1,columnspan=2,padx=10,pady=10)
    
    email_label=Label(invoice_frame,text='Email: ',font=13,bg='#D6E6EA')
    email_label.grid(row=3,column=0,padx=20,pady=10)
    email_entry=Entry(invoice_frame)
    email_entry.grid(row=3,column=1,columnspan=2,padx=10,pady=10)

    address_label = Label(invoice_frame, text='Address: ', font=13,bg='#D6E6EA')
    address_label.grid(row=4, column=0, padx=20, pady=10, sticky='n')
    address_entry = Text(invoice_frame, height=3, width=30)
    address_entry.grid(row=4, column=1, columnspan=2, padx=20, pady=10)

    description_label = Label(invoice_frame, text='Description: ', font=13,bg='#D6E6EA')
    description_label.grid(row=5, column=0, padx=20, pady=10, sticky='n')
    description_entry = Text(invoice_frame, height=5, width=30)
    description_entry.grid(row=5, column=1, columnspan=2, padx=20, pady=10)
    

    button_suppliers_frame=Frame(invoice_frame,bg='#D6E6EA')
    button_suppliers_frame.grid(row=7,column=0,columnspan=3,padx=70)

    save_button=Button(button_suppliers_frame,text='Save',bg='#2B7075',fg='white',command=lambda:save_supplier())
    save_button.grid(row=0,column=0,padx=10,pady=10)

    update_button=Button(button_suppliers_frame,text='Update',bg='#2B7075',fg='white',command=lambda:update_supplier_func(invoice_entry.get(),supplier_entry.get(),contact_entry.get(),email_entry.get(),address_entry.get(1.0,END),description_entry.get(1.0,END)))
    update_button.grid(row=0,column=1,padx=10,pady=10)

    delete_button=Button(button_suppliers_frame,text='Delete',bg='#2B7075',fg='white',command=lambda:delete_function(invoice_entry.get()))
    delete_button.grid(row=0,column=2,padx=10,pady=10)

    clear_button=Button(button_suppliers_frame,text='Clear',bg='#2B7075',fg='white',command=lambda:clear_function(invoice_entry,supplier_entry,contact_entry,email_entry,address_entry,description_entry,True))
    clear_button.grid(row=0,column=3,padx=10,pady=10)
    
    search_supplier_frame=Frame(supplier_dashboard,bg='#D6E6EA')
    search_supplier_frame.place(x=560,y=150,width=670,relheight=1)

    invoice_label=Label(search_supplier_frame,text='Invoice No: ',font=13,bg='#D6E6EA')
    invoice_label.grid(row=0,column=0,padx=20)
    invoice_search_entry=Entry(search_supplier_frame)
    invoice_search_entry.grid(row=0,column=1,columnspan=2,padx=10,pady=10)

    search_button=Button(search_supplier_frame,text='Search',bg='blue',fg='white',font=('times new roman',13),command=lambda:search_function(invoice_search_entry.get()))
    search_button.grid(row=0,column=3,padx=10)

    showAll_button=Button(search_supplier_frame,bg='blue',fg='white',font=('times new roman',13),text='Show All',command=lambda:preview_supplier_data())
    showAll_button.grid(row=0,column=4,padx=10)

    preview_frame=Frame(search_supplier_frame,bg='#DADADA')
    preview_frame.place(x=0,y=50,width=660,height=400)
    horizontal_sb=Scrollbar(preview_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(preview_frame,orient=VERTICAL)
    supplier_search_preview = ttk.Treeview(preview_frame, show='headings',yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    horizontal_sb.pack(side=BOTTOM,fill=X)
    vertical_sb.pack(side=RIGHT,fill=Y)
    supplier_search_preview.pack()
    horizontal_sb.config(command=supplier_search_preview.xview)
    vertical_sb.config(command=supplier_search_preview.yview)

    columns=('invoice_no','suppName','suppContact','suppEmail','suppAddress','suppDescription')
    supplier_search_preview['columns'] = columns

    supplier_search_preview.heading('invoice_no', text='Invoice No.')
    supplier_search_preview.heading('suppName', text='Name')
    supplier_search_preview.heading('suppContact', text='Contact')
    supplier_search_preview.heading('suppEmail', text='Email')
    supplier_search_preview.heading('suppAddress', text='Address')
    supplier_search_preview.heading('suppDescription', text='Description')

    supplier_search_preview.column('invoice_no',width=70)
    supplier_search_preview.column('suppName',width=140)
    supplier_search_preview.column('suppContact',width=150)
    supplier_search_preview.column('suppEmail',width=150)
    supplier_search_preview.column('suppAddress',width=200)
    supplier_search_preview.column('suppDescription',width=400)

    preview_supplier_data()
    update_treeview_data()

    supplier_search_preview.bind('<ButtonRelease-1>',lambda event: select_supplier(event,invoice_entry,supplier_entry,contact_entry,email_entry,address_entry,description_entry))

    return supplier_dashboard