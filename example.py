import tkinter as tk
from tkinter import ttk, END

def select_cart_item(event):
    selected_item = cart.selection()
    if selected_item:
        item_values = cart.item(selected_item[0])['values']
        print("Item values:", item_values)

        name_entry.delete(0, END)
        name_entry.insert(0, item_values[1])

        price_entry.delete(0, END)
        price_entry.insert(0, item_values[2])

        qty_entry.delete(0, END)
        qty_entry.insert(0, item_values[4])

        discount_entry.delete(0, END)
        discount_entry.insert(0, item_values[3])

root = tk.Tk()

# Entry widgets
name_entry = tk.Entry(root)
price_entry = tk.Entry(root)
qty_entry = tk.Entry(root)
discount_entry = tk.Entry(root)

name_entry.pack()
price_entry.pack()
qty_entry.pack()
discount_entry.pack()

# Treeview
cart = ttk.Treeview(root, columns=('id', 'name', 'price', 'discount', 'qty', 'total'), show='headings')
for col in ('id', 'name', 'price', 'discount', 'qty', 'total'):
    cart.heading(col, text=col)

# Dummy Data
cart.insert('', 'end', values=(1, 'Apple', 10, 1, 2, 18))
cart.insert('', 'end', values=(2, 'Banana', 5, 0, 5, 25))

cart.pack()

cart.bind('<<TreeviewSelect>>', select_cart_item)

root.mainloop()
