import tkinter as tk
from tkinter import simpledialog, messagebox
import csv
import os
from datetime import datetime

FILE_NAME = "expenses.csv"
category_totals = {}

# Initial categories
CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills", "Entertainment",
    "Health", "Education", "Groceries", "Other"
]

# Save expense
def save_expense():
    amount = amount_entry.get().strip()
    category = category_var.get()
    note = note_entry.get().strip()

    if not amount or category == "Select Category":
        messagebox.showerror("Error", "Please fill amount and select category!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date_time, amount, category, note])

    amount_entry.delete(0, tk.END)
    category_var.set("Select Category")
    note_entry.delete(0, tk.END)
    load_expenses()

# Load expenses
def load_expenses(search_text=""):
    expenses_list.delete(0, tk.END)
    total = 0
    category_totals.clear()

    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and len(row) >= 4:
                    date_time, amount, category, note = row
                    if search_text.lower() in category.lower() or search_text.lower() in note.lower():
                        expenses_list.insert(tk.END, f"{date_time} | ₹{amount} | {category} ({note})")
                    total += float(amount)
                    category_totals[category] = category_totals.get(category, 0) + float(amount)

    total_label.config(text=f"Total: ₹{total}")

# Delete expense
def delete_expense():
    selected = expenses_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select an expense to delete!")
        return

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
    if not confirm:
        return

    index = selected[0]
    with open(FILE_NAME, "r") as file:
        expenses = list(csv.reader(file))

    visible_items = expenses_list.get(0, tk.END)
    item_to_delete = visible_items[index]
    for i, exp in enumerate(expenses):
        if exp and f"{exp[0]} | ₹{exp[1]} | {exp[2]} ({exp[3]})" == item_to_delete:
            del expenses[i]
            break

    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(expenses)

    load_expenses(search_entry.get().strip())

# Show category totals
def show_category_totals():
    if not category_totals:
        messagebox.showinfo("Category Totals", "No expenses found!")
        return
    msg = "\n".join([f"{cat}: ₹{amt}" for cat, amt in category_totals.items()])
    messagebox.showinfo("Category Totals", msg)

# Search expenses
def search_expenses():
    load_expenses(search_entry.get().strip())

# Add new category
def add_category():
    new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
    if new_cat:
        new_cat = new_cat.strip()
        if new_cat and new_cat not in CATEGORIES:
            CATEGORIES.append(new_cat)
            update_category_menu()
            category_var.set(new_cat)
        elif new_cat in CATEGORIES:
            messagebox.showinfo("Info", f"'{new_cat}' already exists.")

# Update category dropdown
def update_category_menu():
    menu = category_menu["menu"]
    menu.delete(0, "end")
    menu.add_command(label="Select Category", command=lambda: category_var.set("Select Category"))
    for cat in CATEGORIES:
        menu.add_command(label=cat, command=lambda value=cat: category_var.set(value))

# Main window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("350x600")

# Input Frame
frame_input = tk.Frame(root)
frame_input.pack(pady=5, fill="x")

tk.Label(frame_input, text="Amount (₹):").pack(anchor="w")
amount_entry = tk.Entry(frame_input)
amount_entry.pack(fill="x")

tk.Label(frame_input, text="Category:").pack(anchor="w")
category_var = tk.StringVar()
category_var.set("Select Category")
category_menu = tk.OptionMenu(frame_input, category_var, *CATEGORIES)
category_menu.pack(fill="x", pady=(0, 5))
tk.Button(frame_input, text="Add New Category", command=add_category, bg="lightyellow").pack(fill="x", pady=(0, 5))

tk.Label(frame_input, text="Note:").pack(anchor="w")
note_entry = tk.Entry(frame_input)
note_entry.pack(fill="x")

tk.Button(frame_input, text="Add Expense", command=save_expense, bg="lightgreen").pack(fill="x", pady=5)

# Search Frame
frame_search = tk.Frame(root)
frame_search.pack(pady=5, fill="x")

tk.Label(frame_search, text="Search:").pack(side=tk.LEFT)
search_entry = tk.Entry(frame_search)
search_entry.pack(side=tk.LEFT, expand=True, fill="x")
tk.Button(frame_search, text="Go", command=search_expenses, bg="lightblue").pack(side=tk.LEFT)

# Expense List with Scrollbar
list_frame = tk.Frame(root)
list_frame.pack(pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

expenses_list = tk.Listbox(list_frame, width=50, height=12, yscrollcommand=scrollbar.set)
expenses_list.pack(side=tk.LEFT, fill="both", expand=True)
scrollbar.config(command=expenses_list.yview)

# Buttons Frame
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Delete Selected", command=delete_expense, bg="tomato").pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Category Totals", command=show_category_totals, bg="orange").pack(side=tk.LEFT, padx=5)

# Total Label
total_label = tk.Label(root, text="Total: ₹0", font=("Arial", 12, "bold"))
total_label.pack(pady=5)

# Load initial data
load_expenses()
update_category_menu()

root.mainloop()