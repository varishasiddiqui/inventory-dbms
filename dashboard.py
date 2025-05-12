from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import simpledialog, messagebox
import pymysql
from employee_page import employee_form
from supplier_dashboard import supplier_form
from supplier_dashboard import count_supplier
from category_page import count_category
from sales import count_sales
from category_page import category_form
from products_page import product_form
from tax import tax_form
from connect import connect_database
import time
from sales import sales_form
from bill import bill_form
from bill import logout
from deleted import deleted

def dashboard_run():
    global curr_frame, previous_frame
    curr_frame = None  # To store the current frame
    previous_frame = None  # To store the previous frame


    def show_dashboard(root):

        for widget in root.winfo_children():
            widget.destroy()

        frame_products=Frame(root,bg='#002A37')
        frame_products.place(x=350,y=125,width=250,height=450)
        product_icon=PhotoImage(file='C:/Users/PC/Downloads/product_icon.png')
        product_icon_label=Label(frame_products,image=product_icon,bg='#002A37')
        product_icon_label.place(relx=0.5,y=20,anchor='n')
        product_text_label=Label(frame_products,text='Total Products',font=('Helvetica',15),bg='#002A37',fg='white')
        product_text_label.place(y=90,relx=0.5,anchor='n')
        product_count_label=Label(frame_products,text='0',font=('Times New Roman',60),bg='#002A37',fg='white')
        product_count_label.place(y=150,relx=0.5,anchor='n')

        frame_categories=Frame(root,bg='#2B7075')
        frame_categories.place(x=650,y=170,width=250,height=450)
        category_icon=PhotoImage(file='C:/Users/PC/Downloads/category_icon.png')
        category_icon_label=Label(frame_categories,image=category_icon,bg='#2B7075')
        category_icon_label.place(relx=0.5,y=20,anchor='n')
        category_text_label=Label(frame_categories,text='All Categories',font=('Helvetica',15),bg='#2B7075',fg='white')
        category_text_label.place(y=90,relx=0.5,anchor='n')
        category_count_label=Label(frame_categories,text='0',font=('Times New Roman',60),bg='#2B7075',fg='white')
        category_count_label.place(y=150,relx=0.5,anchor='n')

        frame_suppliers=Frame(root,bg='#002A37')
        frame_suppliers.place(x=950,y=125,width=250,height=450)
        suppliers_icon=PhotoImage(file='C:/Users/PC/Downloads/suppliers_icon.png')
        suppliers_icon_label=Label(frame_suppliers,image=suppliers_icon,bg='#002A37')
        suppliers_icon_label.place(relx=0.5,y=20,anchor='n')
        suppliers_text_label=Label(frame_suppliers,text='Suppliers',font=('Helvetica',15),bg='#002A37',fg='white')
        suppliers_text_label.place(y=90,relx=0.5,anchor='n')
        suppliers_count_label=Label(frame_suppliers,text='0',font=('Times New Roman',60),bg='#002A37',fg='white')
        suppliers_count_label.place(y=150,relx=0.5,anchor='n')

        frame_sales=Frame(root,bg='#2B7075')
        frame_sales.place(x=1250,y=170,width=250,height=450)
        sales_icon=PhotoImage(file='C:/Users/PC/Downloads/sales_icon.png')
        sales_icon_label=Label(frame_sales,image=sales_icon,bg='#2B7075')
        sales_icon_label.place(relx=0.5,y=20,anchor='n')
        sales_text_label=Label(frame_sales,text='Total Sales',font=('Helvetica',15),bg='#2B7075',fg='white')
        sales_text_label.place(y=90,relx=0.5,anchor='n')
        sales_count_label=Label(frame_sales,text='0',font=('Times New Roman',60),bg='#2B7075',fg='white')
        sales_count_label.place(y=150,relx=0.5,anchor='n')
      
    def update():
        # Update time and date
        time_label = time.strftime('%A %I:%M:%S %p')
        date_label = time.strftime('%B %d \'%Y')
        welcome_label.config(text=f'{time_label}\t\t\t\t\t\t  Welcome \t\t\t\t\t\t {date_label}')
        sales_count=count_sales()
        # Database call
        cursor, connection = connect_database()
        if cursor and connection:
            try:
                cursor.execute("USE inventory_dbms")
                cursor.execute("SELECT COUNT(product_id) FROM product_details")
                product_count = cursor.fetchone()[0]  # Extract the count value
                product_count_label.config(text=f'{product_count}')
                sales_count_label.config(text=f'{sales_count}')
            except Exception as e:
                print("Error fetching product count:", e)
            finally:
                connection.close()
        else:
            print("Connection Error")

        # Schedule next update
        dashboard.after(100, update)  # update every second (1000ms instead of 10ms)

    curr_frame=None
    def show(form):
        global curr_frame
        if curr_frame:
            curr_frame.place_forget()
        curr_frame=form(dashboard)

    dashboard=Tk()

    def update_category_count():
        category_total=count_category()
        category_count_label.config(text=str(category_total))
        category_count_label.after(500,update_category_count)


    def update_supplier_count():
        supplier_total = count_supplier()
        suppliers_count_label.config(text=str(supplier_total))
        suppliers_count_label.after(5000, update_supplier_count) 

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

    Menu_Frame=Frame(dashboard,bg='#7E909A')
    Menu_Frame.place(x=0,y=100,width=300,relheight=1)


    menu_icon=PhotoImage(file='C:/Users/PC/Downloads/StockSmart.png')
    menu_photoframe=Frame(Menu_Frame,width=300,height=250,bg='red')
    menu_photoframe.place(x=0,y=0)
    menu_label = Label(menu_photoframe, image=menu_icon)
    menu_label.place(x=0, y=0)
    dashboard_icon=PhotoImage(file='C:/Users/PC/Downloads/icons8-home-page-24.png')
    dashboard_button=Button(Menu_Frame,image=dashboard_icon,compound=LEFT, padx=20,text='Dashboard',font=20,bg='#7E909A',fg='#001722',anchor='w')
    dashboard_button.place(y=250,relwidth=1,height=50)
    employees_icon=PhotoImage(file='C:/Users/PC/Downloads/employees_icon.png')
    employees_button=Button(Menu_Frame,image=employees_icon,padx=17,compound=LEFT,text='Employees',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(employee_form))
    employees_button.place(y=300,relwidth=1,height=50)
    supplier_icon=PhotoImage(file='C:/Users/PC/Downloads/supplier_icon.png')
    supplier_button=Button(Menu_Frame,image=supplier_icon,padx=17,compound=LEFT,text='Suppliers',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda: show(supplier_form))
    supplier_button.place(y=350,relwidth=1,height=50)
    category_icon_button=PhotoImage(file='C:/Users/PC/Downloads/category_icon24.png')
    category_button=Button(Menu_Frame,image=category_icon_button,padx=17,compound=LEFT,text='Category',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(category_form))
    category_button.place(y=400,relwidth=1,height=50)
    product_icon_button=PhotoImage(file='C:/Users/PC/Downloads/product_icon24.png')
    product_button=Button(Menu_Frame,image=product_icon_button,padx=17,compound=LEFT,text='Products',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(product_form))
    product_button.place(y=450,relwidth=1,height=50)
    sales_icon_button=PhotoImage(file='C:/Users/PC/Downloads/sales_icon24.png')
    sales_button=Button(Menu_Frame,image=sales_icon_button,padx=17,compound=LEFT,text='Sales',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(sales_form))
    sales_button.place(y=500,relwidth=1,height=50)
    tax_icon_button=PhotoImage(file='C:/Users/PC/Downloads/tax_icon24.png')
    tax_button=Button(Menu_Frame,image=tax_icon_button,padx=17,compound=LEFT,text='Tax',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(tax_form))
    tax_button.place(y=550,relwidth=1,height=50)
    del_icon_button=PhotoImage(file='C:/Users/PC/Downloads/employees_icon.png')
    del_button=Button(Menu_Frame,image=del_icon_button,padx=17,compound=LEFT,text='Deleted Record',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:show(deleted))
    del_button.place(y=600,relwidth=1,height=50)
    logout_icon_button=PhotoImage(file='C:/Users/PC/Downloads/logout_icon.png')
    logout_button=Button(Menu_Frame,image=logout_icon_button,padx=17,compound=LEFT,text='Log Out',font=20,bg='#7E909A',fg='#001722',anchor='w',command=lambda:logout(dashboard))
    logout_button.place(y=650,relwidth=1,height=50)

    
    #the four frames 
    frame_products=Frame(dashboard,bg='#002A37')
    frame_products.place(x=350,y=125,width=250,height=450)
    product_icon=PhotoImage(file='C:/Users/PC/Downloads/product_icon.png')
    product_icon_label=Label(frame_products,image=product_icon,bg='#002A37')
    product_icon_label.place(relx=0.5,y=20,anchor='n')
    product_text_label=Label(frame_products,text='Total Products',font=('Helvetica',15),bg='#002A37',fg='white')
    product_text_label.place(y=90,relx=0.5,anchor='n')
    product_count_label=Label(frame_products,text='0',font=('Times New Roman',60),bg='#002A37',fg='white')
    product_count_label.place(y=150,relx=0.5,anchor='n')

    frame_categories=Frame(dashboard,bg='#2B7075')
    frame_categories.place(x=650,y=170,width=250,height=450)
    category_icon=PhotoImage(file='C:/Users/PC/Downloads/category_icon.png')
    category_icon_label=Label(frame_categories,image=category_icon,bg='#2B7075')
    category_icon_label.place(relx=0.5,y=20,anchor='n')
    category_text_label=Label(frame_categories,text='All Categories',font=('Helvetica',15),bg='#2B7075',fg='white')
    category_text_label.place(y=90,relx=0.5,anchor='n')
    category_count_label=Label(frame_categories,text='0',font=('Times New Roman',60),bg='#2B7075',fg='white')
    category_count_label.place(y=150,relx=0.5,anchor='n')
    update_category_count()

    frame_suppliers=Frame(dashboard,bg='#002A37')
    frame_suppliers.place(x=950,y=125,width=250,height=450)
    suppliers_icon=PhotoImage(file='C:/Users/PC/Downloads/suppliers_icon.png')
    suppliers_icon_label=Label(frame_suppliers,image=suppliers_icon,bg='#002A37')
    suppliers_icon_label.place(relx=0.5,y=20,anchor='n')
    suppliers_text_label=Label(frame_suppliers,text='Suppliers',font=('Helvetica',15),bg='#002A37',fg='white')
    suppliers_text_label.place(y=90,relx=0.5,anchor='n')
    suppliers_count_label=Label(frame_suppliers,text='0',font=('Times New Roman',60),bg='#002A37',fg='white')
    suppliers_count_label.place(y=150,relx=0.5,anchor='n')
    update_supplier_count()

    frame_sales=Frame(dashboard,bg='#2B7075')
    frame_sales.place(x=1250,y=170,width=250,height=450)
    sales_icon=PhotoImage(file='C:/Users/PC/Downloads/sales_icon.png')
    sales_icon_label=Label(frame_sales,image=sales_icon,bg='#2B7075')
    sales_icon_label.place(relx=0.5,y=20,anchor='n')
    sales_text_label=Label(frame_sales,text='Total Sales',font=('Helvetica',15),bg='#2B7075',fg='white')
    sales_text_label.place(y=90,relx=0.5,anchor='n')
    sales_count_label=Label(frame_sales,text='0',font=('Times New Roman',60),bg='#2B7075',fg='white')
    sales_count_label.place(y=150,relx=0.5,anchor='n')
    update()

    dashboard.mainloop()
