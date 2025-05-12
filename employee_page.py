from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
from firebase_config import *

def preview_data():
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_dbms')
    try:
        cursor.execute('SELECT * FROM employee_details')
        emp_records=cursor.fetchall()
        employee_search_preview.delete(*employee_search_preview.get_children())
        for r in emp_records:
            employee_search_preview.insert('',END,values=r)
    except Exception as e:
        messagebox.showerror('Error',f'{e}')
    finally:
        cursor.close()
        connection.close()

def insert_data():
    id=empid_entry.get()
    name=name_entry.get().lower()
    dob=dob_combo.get()
    contact=contact_entry.get()
    email=email_entry.get()
    designation=des_entry.get().lower()
    department=dep_combo.get().lower()
    work_shift=shift_combo.get().lower()
    doj=doj_combo.get()
    salary=salary_entry.get()
    address = add_entry.get("1.0", "end-1c").lower()
    status=status_combo.get().lower()
    gender=gender_combo.get().lower()
    education=edu_combo.get().lower()
    nationality=nation_entry.get().lower()
    emptype=type_combo.get().lower()
    user_type=user_combo.get().lower()
    password=pass_entry.get()
    return id,name,dob,contact,email,designation,department,work_shift,doj, salary ,address,status,gender,education,nationality,emptype,user_type,password

from firebase_config import add_employee_to_firestore

def add_employee():
    id, name, dob, contact, email, designation, department, work_shift, doj, salary, address, status, gender, education, nationality, emptype, user_type, password = insert_data()
    
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    
    if not id:
        cursor.execute("SELECT MAX(empId) FROM employee_details")
        last_empid = cursor.fetchone()[0]
        new_empid = 1 if last_empid is None else last_empid + 1
        empid_entry.insert(0, str(new_empid))
        id = str(new_empid)

    required_fields = [
        (name, 'Please enter employee name'),
        (contact, 'Please enter employee contact'),
        (email, 'Please enter employee email'),
        (designation, 'Please select employee designation'),
        (department, 'Please select employee department'),
        (work_shift, 'Please select employee shift'),
        (salary, 'Please enter employee salary'),
        (status, 'Please enter employee status'),
        (education, 'Please enter employee education'),
        (nationality, 'Please enter employee nationality'),
        (emptype, 'Please enter employee service type'),
        (user_type, 'Please enter employee account type'),
        (password, 'Please enter employee password')
    ]

    for value, error_message in required_fields:
        if not value:
            messagebox.showerror('Error', error_message)
            return

    cursor.execute("SELECT COUNT(*) FROM employee_details WHERE empEmail = %s", (email,))
    ecount = cursor.fetchone()[0]
    if ecount > 0:
        messagebox.showerror('Error', 'Email is already taken')
        return

    cursor.execute("SELECT COUNT(*) FROM employee_details WHERE empPassword = %s", (password,))
    pcount = cursor.fetchone()[0]
    if pcount > 0:
        messagebox.showerror('Error', 'Password is already taken')
        return

    cursor.execute('USE inventory_dbms')
    try:
        cursor.execute('''INSERT INTO employee_details (empID, empName, empDob, empContact, empEmail, empDesig, empDep, 
                             empWork_shift, empDoj, empSalary, empAddress, empStatus, empGender, 
                             empEducation, empNationality, empType, empUser_type, empPassword) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                           (id, name, dob, contact, email, designation, department, work_shift, doj, salary, address,
                            status, gender, education, nationality, emptype, user_type, password))
        connection.commit()
        preview_data()
        messagebox.showinfo('Success', 'Employee added successfully!')

        # Now call Firebase function to add the employee to Firestore as well
        employee_data = {
            'empID': id,
            'empName': name,
            'empDob': dob,
            'empContact': contact,
            'empEmail': email,
            'empDesig': designation,
            'empDep': department,
            'empWork_shift': work_shift,
            'empDoj': doj,
            'empSalary': salary,
            'empAddress': address,
            'empStatus': status,
            'empGender': gender,
            'empEducation': education,
            'empNationality': nationality,
            'empType': emptype,
            'empUser_type': user_type,
            'empPassword': password
        }
        
        add_employee_to_firestore(id, name, dob, contact, email, designation, department, work_shift, doj, salary, address, status, gender, education, nationality, emptype, user_type, password)

    except Exception as e:
        messagebox.showerror('Error', f"Database error: {str(e)}")

def clear_function(empid_entry,name_entry,dob_combo,contact_entry,email_entry,des_entry,dep_combo,shift_combo,doj_combo,salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry,clear):
    empid_entry.delete(0,END)
    name_entry.delete(0,END)
    dob_combo.set_date(date.today())
    gender_combo.set('Male/Female')
    contact_entry.delete(0,END)
    email_entry.delete(0,END)
    des_entry.delete(0,END)
    dep_combo.set('Department')
    shift_combo.set('Shift')
    doj_combo.set_date(date.today())
    salary_entry.delete(0,END)
    add_entry.delete(1.0,END)
    status_combo.set('Relationship Status')
    edu_combo.set('Education')
    nation_entry.delete(0,END)
    type_combo.set('Type')
    user_combo.set('User Type')
    pass_entry.delete(0,END)
    if clear:
        employee_search_preview.selection_remove(employee_search_preview.selection())


def select_emp_data(event,empid_entry,name_entry,dob_combo,contact_entry,email_entry,
    des_entry,dep_combo,shift_combo,doj_combo,salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry):
    index=employee_search_preview.selection()
    content=employee_search_preview.item(index)
    values=content['values']
    clear_function(empid_entry,name_entry,dob_combo,contact_entry,email_entry,
    des_entry,dep_combo,shift_combo,doj_combo,salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry,False)
    empid_entry.insert(0,values[0])
    name_entry.insert(0,values[1])
    dob_combo.set_date(values[2])
    contact_entry.insert(0,values[3])
    email_entry.insert(0,values[4])
    des_entry.insert(0,values[5])
    dep_combo.set(values[6])
    shift_combo.set(values[7])
    doj_combo.set_date(values[8])
    salary_entry.insert(0,values[9])
    add_entry.insert(1.0,values[10])
    status_combo.set(values[11])
    gender_combo.set(values[12])
    edu_combo.set(values[13])
    nation_entry.insert(0,values[14])
    type_combo.set(values[15])
    user_combo.set(values[16])
    pass_entry.insert(0,values[17])

    

def update_function(id, name, dob, contact, email, designation, department, work_shift, doj, salary, address, status, gender, education, nationality, type, user_type, password):
    select = employee_search_preview.selection()
    if not select:
        messagebox.showerror('Error', 'No employee is selected!')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try: 
            cursor.execute('USE inventory_dbms')
            cursor.execute('SELECT * FROM employee_details WHERE empId=%s', (id,))
            currData = cursor.fetchone()
            currData = currData[1:]  # Exclude the empId

            new = (name, dob, contact, email, designation, department, work_shift, doj, salary, address, status, gender, education, nationality, type, user_type, password)
            
            if currData == new:
                messagebox.showinfo('Info:', 'Nothing to Update!')
            else:
                cursor.execute('''
                    UPDATE employee_details SET
                    empName=%s,
                    empDob=%s,
                    empContact=%s,
                    empEmail=%s,
                    empDesig=%s,
                    empDep=%s,
                    empWork_shift=%s,
                    empDoj=%s,
                    empSalary=%s,
                    empAddress=%s,
                    empStatus=%s,
                    empGender=%s,
                    empEducation=%s,
                    empNationality=%s,
                    empType=%s,
                    empUser_type=%s,
                    empPassword=%s
                    WHERE empId=%s
                ''', (
                    name, dob, contact, email, designation, department, work_shift, doj,
                    salary, address, status, gender, education, nationality, type,
                    user_type, password, id
                ))
                connection.commit()
                messagebox.showinfo('UPDATED', f'Details updated for Employee: {id}')
                preview_data()

                # Now call Firestore function to update the employee details
                updated_data = {
                    'empName': name,
                    'empDob': dob,
                    'empContact': contact,
                    'empEmail': email,
                    'empDesig': designation,
                    'empDep': department,
                    'empWork_shift': work_shift,
                    'empDoj': doj,
                    'empSalary': salary,
                    'empAddress': address,
                    'empStatus': status,
                    'empGender': gender,
                    'empEducation': education,
                    'empNationality': nationality,
                    'empType': type,
                    'empUser_type': user_type,
                    'empPassword': password
                }

                # Call Firebase function to update the employee in Firestore
                update_employee_in_firestore(id, updated_data)

        except Exception as e:
            messagebox.showerror('Error', f'{e}')
        finally:
            cursor.close()
            connection.close()


def delete_function(id=None, name=None):
    # Fetch selected rows
    sel = employee_search_preview.selection()

    if not sel:
        messagebox.showerror('Error', 'Nothing to Delete! Kindly select a row.')
        return

    # If no id or name passed, ask the user for confirmation for each selected row
    response = messagebox.askquestion('Attention', f'Do you really want to delete the selected employee records?').lower()

    if response != 'yes':
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        for selected_item in sel:  # Loop through selected rows
            # Get the employee ID from the selected row
            emp_id = employee_search_preview.item(selected_item, 'values')[0]  # Assuming empId is the first column

            # Fetch the record to be deleted
            cursor.execute('SELECT * FROM employee_details WHERE empId = %s', (emp_id,))
            delete_emp = cursor.fetchone()

            if not delete_emp:
                messagebox.showerror('Error', f'No matching employee found for ID {emp_id}.')
                continue  # Skip this row if not found

            # Insert into deleted employees table
            cursor.execute(''' 
                INSERT INTO employee_del (empId, empName, empDob, empContact, empEmail, empDesig, empDep,
                empWork_shift, empDoj, empSalary, empAddress, empStatus, empGender, empEducation,
                empNationality, empType, empUser_type, empPassword)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', delete_emp)

            # Delete from original table
            cursor.execute('DELETE FROM employee_details WHERE empId = %s', (emp_id,))

            # Call the Firebase delete function
            delete_employee_from_firestore(emp_id)
        
        connection.commit()

        messagebox.showinfo('Done', 'Selected employee records have been successfully deleted!')
        preview_data()  # Refresh the display

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')
    finally:
        cursor.close()
        connection.close()




def search_function(s,value):
    if s=="Search Employee By" or value == '':
        messagebox.showerror('Error','Either "Search By" or "Value To Be Searched" is not given!')
    else:
        cursor,connection=connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_dbms')
            cursor.execute(f'SELECT * FROM employee_details WHERE {s} LIKE %s', f'%{value}%')
            search=cursor.fetchall()
            employee_search_preview.delete(*employee_search_preview.get_children())
            for record in search:
                employee_search_preview.insert('',END,value=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error: {e}')
        finally:
            cursor.close()
            connection.close()


def employee_form(dashboard):
    global empid_entry, name_entry, dob_combo, contact_entry, email_entry,des_entry,dep_combo,shift_combo,doj_combo
    global salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry,employee_search_preview

    employee_dashboard=Frame(dashboard,bg='#D6E6EA')
    employee_dashboard.place(x=300,y=100,width=1230, relheight=1)
    employee_heading_label=Label(employee_dashboard,text='EMPLOYEE DETAILS',font=('Times New Roman',20,'bold'),bg='#2B707F',fg='white')
    employee_heading_label.place(x=0,y=0,relwidth=1)
    prev_button=Button(employee_dashboard,text='Go Back',font=('Courier New',10,'italic'),fg='#002A37',bg='#D6E6EA',bd=0,command=lambda: employee_dashboard.place_forget())
    prev_button.place(x=0,y=38)
    
    search_frame_employee = Frame(employee_dashboard, bg='#D6E6EA')
    search_frame_employee.place(relx=0.5,y=60, anchor="n")
    search_employee_combo = ttk.Combobox(search_frame_employee, values=('empId', 'empName', 'empEmail','emoDob','empdesig','empDoj,'
    'empDep','empUser_type','empType','empGender','empSalary','empNationality','empContact','empWork_shift','empEducation','empStatus'), font=12, state='readonly', justify='left')
    search_employee_combo.set('Search Employee By')
    search_employee_combo.grid(row=0, column=0, padx=(50, 5), pady=10) 

    search_find = Entry(search_frame_employee, font=12)
    search_find.grid(row=0, column=1, padx=5, pady=10)

    search_icon = PhotoImage(file='C:/Users/PC/Downloads/search_icon.png')
    search_button = Button(search_frame_employee, image=search_icon, bg='#045866',command=lambda: search_function(search_employee_combo.get(),search_find.get()))
    search_button.image = search_icon 
    search_button.grid(row=0, column=2, padx=5, pady=10)

    showAll_button = Button(search_frame_employee, text='Show All', fg='white', bg='#045866',command=lambda:preview_data())
    showAll_button.grid(row=0, column=3, padx=5, pady=10)
    
    preview_frame=Frame(employee_dashboard)
    preview_frame.place(x=0,y=100,width=1230,height=200)
    horizontal_sb=Scrollbar(preview_frame,orient=HORIZONTAL)
    vertical_sb=Scrollbar(preview_frame,orient=VERTICAL)
    employee_search_preview = ttk.Treeview(preview_frame, show='headings',yscrollcommand=vertical_sb.set,xscrollcommand=horizontal_sb.set)
    horizontal_sb.pack(side=BOTTOM,fill=X)
    vertical_sb.pack(side=RIGHT,fill=Y)
    employee_search_preview.pack()
    horizontal_sb.config(command=employee_search_preview.xview)
    vertical_sb.config(command=employee_search_preview.yview)

    columns = ('emp_id', 'emp_name', 'emp_dob', 'emp_con', 'emp_email', 'emp_des', 'emp_dep', 
           'emp_shift', 'emp_doj', 'emp_salary', 'emp_address','emp_status', 'emp_gender','emp_edu', 'emp_nationality', 'emp_type','user_type','pass')

    employee_search_preview['columns'] = columns



    employee_search_preview.heading('emp_id', text='ID')
    employee_search_preview.heading('emp_name', text='Name')
    employee_search_preview.heading('emp_dob', text='DOB')
    employee_search_preview.heading('emp_con', text='Contact')
    employee_search_preview.heading('emp_email', text='Email')
    employee_search_preview.heading('emp_des', text='Designation')
    employee_search_preview.heading('emp_dep', text='Department')
    employee_search_preview.heading('emp_shift', text='Work Shift')
    employee_search_preview.heading('emp_doj', text='Date of Joining')
    employee_search_preview.heading('emp_salary', text='Salary')
    employee_search_preview.heading('emp_address', text='Address')
    employee_search_preview.heading('emp_gender', text='Gender')
    employee_search_preview.heading('emp_nationality', text='Nationality')
    employee_search_preview.heading('emp_type', text='Type')
    employee_search_preview.heading('emp_edu', text='Education')
    employee_search_preview.heading('emp_status', text='Status')
    employee_search_preview.heading('user_type', text='User Type')
    employee_search_preview.heading('pass', text='Password')

    employee_search_preview.column('emp_id',width=40)
    employee_search_preview.column('emp_name',width=100)
    employee_search_preview.column('emp_dob',width=100)
    employee_search_preview.column('emp_con',width=100)
    employee_search_preview.column('emp_email',width=150)
    employee_search_preview.column('emp_des',width=100)
    employee_search_preview.column('emp_dep',width=100)
    employee_search_preview.column('emp_shift',width=70)
    employee_search_preview.column('emp_doj',width=100)
    employee_search_preview.column('emp_salary',width=50)
    employee_search_preview.column('emp_address',width=150)
    employee_search_preview.column('emp_gender',width=30)
    employee_search_preview.column('emp_nationality',width=150)
    employee_search_preview.column('emp_type',width=150)

    preview_data()
    

    bottom_frame=Frame(employee_dashboard,bg='#D6E6EA')
    bottom_frame.place(x=0,y=300,relwidth=1,height=300)

    bott_empid_label=Label(bottom_frame,text='Emp ID:',bg='#D6E6EA',font='bold',justify='left')
    bott_empid_label.grid(row=0,column=0,padx=20)
    empid_entry=Entry(bottom_frame)
    empid_entry.grid(row=0,column=1,padx=5,pady=20)

    bott_name_label=Label(bottom_frame,text='Name:',bg='#D6E6EA',font='bold',justify='left')
    bott_name_label.grid(row=1,column=0,padx=5)
    name_entry=Entry(bottom_frame)
    name_entry.grid(row=1,column=1)

    bott_gender_label=Label(bottom_frame,text='Gender:',font='bold',bg='#D6E6EA')
    bott_gender_label.grid(row=0,column=2,padx=5)
    gender_combo=ttk.Combobox(bottom_frame,values=('M','F'),state='readonly')
    gender_combo.set('Male/Female')
    gender_combo.grid(row=0,column=3,padx=5)

    bott_dob_label=Label(bottom_frame,text='Date Of Birth:',bg='#D6E6EA',font='bold')
    bott_dob_label.grid(row=1,column=2,padx=5)
    dob_combo=DateEntry(bottom_frame)
    dob_combo.grid(row=1,column=3)

    bott_con_label=Label(bottom_frame,text='Contact:',bg='#D6E6EA',font='bold')
    bott_con_label.grid(row=2,column=0,padx=5)
    contact_entry=Entry(bottom_frame)
    contact_entry.grid(row=2,column=1)

    bott_email_label=Label(bottom_frame,text='Email:',bg='#D6E6EA',font='bold')
    bott_email_label.grid(row=4,column=0,padx=5)
    email_entry=Entry(bottom_frame)
    email_entry.grid(row=4,column=1)

    bott_des_label=Label(bottom_frame,text='Designation:',bg='#D6E6EA',font='bold')
    bott_des_label.grid(row=3,column=2,padx=5)
    des_entry=Entry(bottom_frame)
    des_entry.grid(row=3,column=3)

    bott_dep_label=Label(bottom_frame,text='Department:',font='bold',bg='#D6E6EA')
    bott_dep_label.grid(row=2,column=2,padx=5)
    dep_combo=ttk.Combobox(bottom_frame,values=('Procurement','Warehouse','Stock Management','Sales & Order Management','Logistics & Distribution','Finance & Accounting','Customer Support','Administration'),state='readonly')
    dep_combo.set('Department')
    dep_combo.grid(row=2,column=3,padx=5)

    bott_type_label=Label(bottom_frame,text='Type:',font='bold',bg='#D6E6EA')
    bott_type_label.grid(row=3,column=0,padx=5)
    type_combo=ttk.Combobox(bottom_frame,values=('Full-Time','Part-Time','Contract','Intern'),state='readonly')
    type_combo.set('Type')
    type_combo.grid(row=3,column=1,padx=5)

    bott_shift_label=Label(bottom_frame,text='Shift:',font='bold',bg='#D6E6EA')
    bott_shift_label.grid(row=0,column=4,padx=5)
    shift_combo=ttk.Combobox(bottom_frame,values=('Day','Night'),state='readonly')
    shift_combo.set('Shift')
    shift_combo.grid(row=0,column=5,padx=5)

    bott_sal_label=Label(bottom_frame,text='Salary:',bg='#D6E6EA',font='bold')
    bott_sal_label.grid(row=1,column=4,padx=5)
    salary_entry=Entry(bottom_frame)
    salary_entry.grid(row=1,column=5)

    bott_doj_label=Label(bottom_frame,text='Date Of Joining:',bg='#D6E6EA',font='bold')
    bott_doj_label.grid(row=2,column=4,padx=20)
    doj_combo=DateEntry(bottom_frame)
    doj_combo.grid(row=2,column=5)

    bott_edu_label=Label(bottom_frame,text='Education:',bg='#D6E6EA',font='bold')
    bott_edu_label.grid(row=3,column=4,padx=5)
    edu_combo=ttk.Combobox(bottom_frame,values=('Intermediate','Bachelors','Masters','PhD'))
    edu_combo.set('Education')
    edu_combo.grid(row=3,column=5)

    bott_status_label=Label(bottom_frame,text='Status',bg='#D6E6EA',font='bold')
    bott_status_label.grid(row=0,column=6)
    status_combo=ttk.Combobox(bottom_frame,values=('Single','Married','Divorced','Widowed','Separated','Engaged'))
    status_combo.set('Relationship Status')
    status_combo.grid(row=0,column=7)

    bott_nation_label=Label(bottom_frame,text='Nationality:',bg='#D6E6EA',font='bold')
    bott_nation_label.grid(row=1,column=6)
    nation_entry=Entry(bottom_frame)
    nation_entry.grid(row=1,column=7)

    bott_add_label=Label(bottom_frame,text='Address:',bg='#D6E6EA',font='bold')
    bott_add_label.grid(row=2,column=6)
    add_entry=Text(bottom_frame,width=20,height=3)
    add_entry.grid(row=2,column=7,rowspan=2)

    bott_user_label=Label(bottom_frame,text='User Type',bg='#D6E6EA',font='bold')
    bott_user_label.grid(row=4,column=4)
    user_combo=ttk.Combobox(bottom_frame,values=('Admin','Employee'))
    user_combo.set('User Type')
    user_combo.grid(row=4,column=5)

    bott_pass_label=Label(bottom_frame,text='Password:',bg='#D6E6EA',font='bold')
    bott_pass_label.grid(row=4,column=2)
    pass_entry=Entry(bottom_frame)
    pass_entry.grid(row=4,column=3)

    button_frame=Button(bottom_frame,text='Add Employee',bg='#2B7075',fg='white',command=add_employee)
    button_frame.grid(row=8,column=2,columnspan=2,pady=40)
    
    button_frame=Button(bottom_frame,text='Delete Employee',bg='#2B7075',fg='white',command=lambda:delete_function(empid_entry.get(), name_entry.get()))
    button_frame.grid(row=8,column=3,columnspan=2,pady=40)
    
    button_frame=Button(bottom_frame,text='Update Employee',bg='#2B7075',fg='white',command=lambda: update_function(empid_entry.get(), name_entry.get(), dob_combo.get(), contact_entry.get(), email_entry.get(),
        des_entry.get(), dep_combo.get(), shift_combo.get(), doj_combo.get(), salary_entry.get(),
        add_entry.get("1.0","end-1c"), status_combo.get(), gender_combo.get(), edu_combo.get(), nation_entry.get(),
        type_combo.get(), user_combo.get(), pass_entry.get()))
    button_frame.grid(row=8,column=4,columnspan=2,pady=40)
    
    button_frame=Button(bottom_frame,text='  Clear  ',bg='#2B7075',fg='white',command=lambda: clear_function(empid_entry,name_entry,dob_combo,contact_entry,email_entry,
    des_entry,dep_combo,shift_combo,doj_combo,salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry,True))
    button_frame.grid(row=8,column=5,columnspan=2,pady=40)

    employee_search_preview.bind('<ButtonRelease-1>',lambda event: select_emp_data(event,empid_entry,name_entry,dob_combo,contact_entry,email_entry,
    des_entry,dep_combo,shift_combo,doj_combo,salary_entry,add_entry,status_combo,gender_combo,edu_combo,nation_entry,type_combo,user_combo,pass_entry))

    return employee_dashboard