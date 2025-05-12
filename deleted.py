from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database

def deleted(dashboard):
    del_dashboard = Frame(dashboard, bg='#D6E6EA')
    del_dashboard.place(x=300, y=100, width=1230, relheight=1)

    Label(del_dashboard, text='Deleted Employee Records (Recycle Bin)', font=('Times New Roman', 20, 'bold'),
          bg='#2B707F', fg='white').place(x=0, y=0, relwidth=1)

    def go_back():
        if messagebox.askyesno("Discard Changes", "Unsaved changes will be lost. Continue?"):
            del_dashboard.place_forget()

    Button(del_dashboard, text='← Go Back', font=('Courier New', 11, 'bold'),
           fg='black', bg='#D6E6EA', bd=0, command=go_back, cursor='hand2').place(x=10, y=40)

    # Treeview for Recycle Bin
    columns = (
        'empId', 'empName', 'empDob', 'empContact', 'empEmail', 'empDesig', 'empDep',
        'empWork_shift', 'empDoj', 'empSalary', 'empAddress', 'empStatus', 'empGender',
        'empEducation', 'empNationality', 'empType', 'empUser_type', 'empPassword'
    )

    recycle_tree = ttk.Treeview(del_dashboard, columns=columns, show='headings', selectmode="extended")  # Allow multiple selection
    recycle_tree.place(x=50, y=90, width=1100, height=500)

    # Set column headings and width
    for col in columns:
        recycle_tree.heading(col, text=col)
        recycle_tree.column(col, width=150)

    # Scrollbar
    scrollbar_y = Scrollbar(del_dashboard, orient=VERTICAL, command=recycle_tree.yview)
    scrollbar_y.place(x=1150, y=90, height=500)
    recycle_tree.configure(yscrollcommand=scrollbar_y.set)

    # Horizontal scrollbar
    scrollbar_x = Scrollbar(del_dashboard, orient=HORIZONTAL, command=recycle_tree.xview)
    scrollbar_x.place(x=50, y=590, width=1100)
    recycle_tree.configure(xscrollcommand=scrollbar_x.set)

    # Load deleted employees from DB
    def load_deleted_employees():
        recycle_tree.delete(*recycle_tree.get_children())
        cursor, connection = connect_database()
        if cursor:
            cursor.execute("SELECT * FROM employee_del")
            for row in cursor.fetchall():
                recycle_tree.insert('', END, values=row)
            connection.close()

    # Right-click menu
    menu = Menu(recycle_tree, tearoff=0)
    menu.add_command(label="Restore", command=lambda: restore_employee())
    menu.add_command(label="Delete Permanently", command=lambda: delete_permanently())

    def right_click(event):
        selected = recycle_tree.identify_row(event.y)
        if selected:
            recycle_tree.selection_set(selected)
            menu.post(event.x_root, event.y_root)

    recycle_tree.bind("<Button-3>", right_click)

    def restore_employee():
        selected_items = recycle_tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Record", "No record selected")
            return
        
        cursor, connection = connect_database()
        if cursor:
            for item in selected_items:
                data = recycle_tree.item(item)['values']
                emp_id = data[0]

                # Check if already exists in employee_details
                cursor.execute("SELECT * FROM employee_details WHERE empId = %s", (emp_id,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate ID", f"Employee ID {emp_id} already exists in the main table.")
                    continue  # Skip to next employee

                # Get full record from employee_del
                cursor.execute("SELECT * FROM employee_del WHERE empId = %s", (emp_id,))
                emp = cursor.fetchone()

                # Insert into employee_details
                cursor.execute(''' 
                    INSERT INTO employee_details (empId, empName, empDob, empContact, empEmail, empDesig, empDep,
                        empWork_shift, empDoj, empSalary, empAddress, empStatus, empGender, empEducation,
                        empNationality, empType, empUser_type, empPassword)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', emp)

                # Delete from employee_del
                cursor.execute("DELETE FROM employee_del WHERE empId = %s", (emp_id,))
            
            connection.commit()
            connection.close()
            load_deleted_employees()
            messagebox.showinfo("Restored", f"Selected employee records restored successfully.")

    def delete_permanently():
        selected_items = recycle_tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Record", "No record selected")
            return

        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {len(selected_items)} records permanently?")
        if confirm:
            cursor, connection = connect_database()
            if cursor:
                for item in selected_items:
                    data = recycle_tree.item(item)['values']
                    emp_id = data[0]
                    cursor.execute("DELETE FROM employee_del WHERE empId = %s", (emp_id,))

                connection.commit()
                connection.close()
                load_deleted_employees()
                messagebox.showinfo("Deleted", f"{len(selected_items)} employee records deleted permanently.")

    load_deleted_employees()
