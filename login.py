from tkinter import *
from tkinter import ttk
import pymysql
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date
from connect import connect_database
import dashboard
from dashboard import dashboard_run
from bill import bill_form
from activity_log import log_employee_login

def login_window():
    root = Tk()
    root.geometry("700x520")
    root.title("Login Page")
    root.resizable(False, False)

    # Left Frame
    Left_photo=PhotoImage(file='C:/Users/PC/Downloads/SMART.png')
    
    left_frame = Frame(root, bg='black')
    left_frame.place(x=0, y=0, width=350, height=520)
    Left_label=Label(left_frame,image=Left_photo)
    Left_label.pack()

    # Right Frame
    right_frame = Frame(root, bg='white')
    right_frame.place(x=350, y=0, width=350, height=520)

    # Login Frame (inside right_frame)
    login_frame = Frame(right_frame, bg='white')
    login_frame.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.6)

    # Title Label
    login_label = Label(login_frame, text='LOGIN ACCOUNT', bg='white', fg='black', font=('Helvetica', 16, 'bold'))
    login_label.pack(pady=10)

    # Username
    username_label = Label(login_frame, text='EMPLOYEE ID', font=('Helvetica', 12), bg='white')
    username_label.pack(pady=(20, 5))
    username_entry = ttk.Entry(login_frame, width=30)
    username_entry.pack(ipady=5)

    # Password
    password_label = Label(login_frame, text='PASSWORD', font=('Helvetica', 12), bg='white')
    password_label.pack(pady=(20, 5))
    password_entry = ttk.Entry(login_frame, show='*', width=30)
    password_entry.pack(ipady=5)

    # Login Button
    login_button = Button(login_frame, text='Login',bg='#00404E',fg='white', command=lambda: login())
    login_button.pack(pady=20, ipadx=10, ipady=5)

    # Forgot Password Label
    forgot_password = Label(login_frame, text="Forgot Password?", fg='blue', bg='white', cursor="hand2", font=('Helvetica', 10, 'underline'))
    forgot_password.pack()

    # Forgot Password Window Function
    def open_forgot_window(event=None):
        # Fetch email from database using the username
        username = username_entry.get()

        if not username:
            messagebox.showwarning("Input Error", "Please enter your username first.")
            return

        cursor, connection = connect_database()
        cursor.execute('USE inventory_system')
        cursor.execute('SELECT empEmail FROM employee_details WHERE empId = %s', (username,))
        row = cursor.fetchone()

        if row:
            email = row[0]
            # Mask the email
            masked_email = email[:3] + "****" + email[email.index('@'):]
            messagebox.showinfo("Password Reset", f"Password reset link has been sent to:\n{masked_email}")  # Close the forgot password window
        else:
            messagebox.showerror("Login Error", "Username not found.") # Close the forgot password window

    # Bind label to open the forgot password window
    forgot_password.bind("<Button-1>", open_forgot_window)

    def login():
        try:
            username = int(username_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Employee ID must be a number.")
            return

        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        cursor, connection = connect_database()
        cursor.execute('USE inventory_dbms')
        cursor.execute('SELECT empId, empPassword, empEmail, empName,empUser_type FROM employee_details')
        rows = cursor.fetchall()

        user_found = False

        for empId, empPassword, empEmail, empName,empUser in rows:
            if username == empId:
                user_found = True
                if password == empPassword:
                    log_employee_login(username)
                    messagebox.showinfo("Login Success", f"Welcome {empName}")
                    root.destroy()
                    if empUser == 'admin':
                        dashboard_run()
                    if empUser=='employee':
                        bill_form()
                    return 
                
                else:
                    # Show incorrect password and hint to click "Forgot Password"
                    messagebox.showerror("Login Error", "Incorrect Password.\nIf you've forgotten your password, click 'Forgot Password?'")
                    return

        if not user_found:
            messagebox.showerror("Login Error", "Username does not exist")
    root.mainloop()
    return 

login_window()