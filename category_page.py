from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
from firebase_config import *

def insert_data():
    cat_id=categoryId_entry.get()
    cat_name=categoryName_entry.get().lower()
    cat_description=categoryDes_entry.get(1.0,END).lower()
    
    return cat_id,cat_name,cat_description

def add():
    id,name,description=insert_data()
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    if not id:
        cursor.execute("SELECT MAX(category_id) FROM category_details")
        last_invoice = cursor.fetchone()[0]
        new_invoice = 1 if last_invoice is None else last_invoice + 1
        categoryId_entry.insert(0, str(new_invoice))
        id=str(new_invoice)
    
    if not name:
        messagebox.showerror('Error', 'Please enter category name')
        return
    if not description:
        messagebox.showerror('Error', 'Please enter description')
        return
    cursor.execute('USE inventory_dbms')
    try:

        cursor.execute('''INSERT INTO category_details(category_id,category_name,category_des) VALUES (%s,%s,%s)''',
        (id,name,description))
        connection.commit()
        add_category_to_firestore(id,name,description)
        messagebox.showinfo('Success', 'Category details saved successfully!')
        preview_data(category_preview)
    except Exception as e:
        messagebox.showerror('Error', f'{e}')



def delete_function(id):
    sel=category_preview.selection()
    if not sel:
        messagebox.showerror('Error','Nothing to Delete! Kindly select a row.')
    else:
        if not id:
            messagebox.showerror('Error','ID field is empty!')
            return
        response=messagebox.askquestion('Attention',f'Do you really want to delete the record for Category ID: {id}?')
        if response=='yes':
            cursor,connection=connect_database()
            if not cursor or not connection:
                return
            cursor.execute('use inventory_dbms')
            cursor.execute('DELETE FROM category_details where category_id=%s',(id,))
            connection.commit()
            preview_data(category_preview)
            messagebox.showinfo('Done',f'Record for Category ID :{id} has been successfully deleted!')


def preview_data(category_preview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_dbms')
    try:
        cursor.execute('SELECT * FROM category_details')
        emp_records=cursor.fetchall()
        category_preview.delete(*category_preview.get_children())
        for r in emp_records:
            category_preview.insert('',END,values=r)
    except Exception as e:
        messagebox.showerror('Error',f'{e}')
    finally:
        cursor.close()
        connection.close()

def count_category():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('SELECT COUNT(category_id) FROM category_details')  
        result=cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        messagebox.showerror('Error', f'{e}')
        return
    finally:
        cursor.close()
        connection.close()

def select_category(event,id,name,description):
    index=category_preview.selection()
    content=category_preview.item(index)
    values=content['values']
    clear_function(id,name,description,False)
    categoryId_entry.insert(0,values[0])
    categoryName_entry.insert(0,values[1])
    categoryDes_entry.insert(INSERT,values[2])

def clear_function(id,name,description,clear):
    id.delete(0,END)
    name.delete(0,END)
    description.delete(1.0,END)
    
    if clear:
        category_preview.selection_remove(category_preview.selection())



def category_form(dashboard):
    global categoryId_entry,categoryName_entry,categoryDes_entry,category_preview

    category_dashboard=Frame(dashboard,bg='#D6E6EA')
    category_dashboard.place(x=300,y=100,width=1230, relheight=1)
    category_heading_label=Label(category_dashboard,text='CATEGORY DETAILS',font=('Times New Roman',20,'bold'),bg='#2B707F',fg='white')
    category_heading_label.place(x=0,y=0,relwidth=1)
    prev_button=Button(category_dashboard,text='Go Back',font=('Courier New',10,'italic'),fg='#002A37',bg='#D6E6EA',bd=0,command=lambda: category_dashboard.place_forget())
    prev_button.place(x=0,y=38)

    inner_frame=Frame(category_dashboard,bg='#D6E6EA')
    inner_frame.place(x=360,y=175,relwidth=0.25,relheight=0.3)
    
    categoryId_label=Label(inner_frame,text='Category ID:',font=('Times New Roman',12),bg='#D6E6EA')
    categoryId_label.grid(row=0,column=0,columnspan=2,padx=10)
    categoryId_entry=Entry(inner_frame)
    categoryId_entry.grid(row=0,column=2,columnspan=2,padx=10,pady=10)

    categoryName_label=Label(inner_frame,text='Category Name:',font=('Times New Roman',12),bg='#D6E6EA')
    categoryName_label.grid(row=1,column=0,columnspan=2,padx=10)
    categoryName_entry=Entry(inner_frame)
    categoryName_entry.grid(row=1,column=2,columnspan=2,padx=10,pady=10)

    categoryDes_label=Label(inner_frame,text='Description:',font=('Times New Roman',12),bg='#D6E6EA')
    categoryDes_label.grid(row=2,column=0,columnspan=2,padx=10)
    categoryDes_entry = Text(inner_frame, width=20, height=3)
    categoryDes_entry.grid(row=2,column=2,padx=10,pady=10)

    operations_frame=Frame(inner_frame,bg='#D6E6EA')
    operations_frame.grid(row=3,column=0,columnspan=4,padx=10,pady=20)
    
    add_button=Button(operations_frame,text='Add',font=('Courier New',10),bg='#2B7075',fg='white',command=lambda:add())
    add_button.grid(row=0,column=0,padx=10)

    delete_button=Button(operations_frame,text='Delete',bg='#2B7075',fg='white',command=lambda:delete_function(categoryId_entry.get()))
    delete_button.grid(row=0,column=1,padx=10)

    clear_button=Button(operations_frame,text='Clear',bg='#2B7075',fg='white',command=lambda:clear_function(categoryId_entry,categoryName_entry,categoryDes_entry,True))
    clear_button.grid(row=0,column=2,padx=10)

    preview_frame=Frame(category_dashboard,bg='#D6E6EA')
    preview_frame.place(x=667.5,y=175,width=550,height=400)
    horizontal_sb=Scrollbar(preview_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(preview_frame,orient=VERTICAL)
    category_preview = ttk.Treeview(preview_frame, show='headings',yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    horizontal_sb.pack(side=BOTTOM,fill=X)
    vertical_sb.pack(side=RIGHT,fill=Y)
    category_preview.pack()
    horizontal_sb.config(command=category_preview.xview)
    vertical_sb.config(command=category_preview.yview)

    columns=('id','name','description')
    category_preview['columns'] = columns

    category_preview.heading('id', text='ID')
    category_preview.heading('name', text='Name')
    category_preview.heading('description', text='Description')

    category_preview.column('id',width=40)
    category_preview.column('name',width=150)
    category_preview.column('description',width=350)

    preview_data(category_preview)

    category_preview.bind('<ButtonRelease-1>',lambda event: select_category(event,categoryId_entry,categoryName_entry,categoryDes_entry))

    return category_dashboard


