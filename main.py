import tkinter as tk
from tkinter import simpledialog, messagebox
import csv
import os
import hashlib
from datetime import datetime

# Files
USERS_FILE = "users.csv"
FILE_NAME = "expenses.csv"

# Default categories
CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills", "Entertainment",
    "Health", "Education", "Groceries", "Other"
]

# Helper: hash password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Ensure user file exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        # header: username, password_hash
        writer.writerow(["username", "password_hash"])

# Ensure expense file exists (header optional)
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as f:
        writer = csv.writer(f)
        # no header to keep old behaviour; rows: datetime, amount, category, note, username
        # we'll add username as 5th column to segregate user data

current_user = None
category_totals = {}

# ---------- Login / Register Windows ----------
def open_login_window():
    # create a small login window
    login_win = tk.Tk()
    login_win.title("ExpenseTracker - Login")
    login_win.geometry("300x220")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Username:").pack(anchor="w", padx=10, pady=(10, 0))
    username_entry = tk.Entry(login_win)
    username_entry.pack(fill="x", padx=10)

    tk.Label(login_win, text="Password:").pack(anchor="w", padx=10, pady=(8, 0))
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(fill="x", padx=10)

    def do_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        pwd_hash = hash_password(password)
        with open(USERS_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2 and row[0] == username and row[1] == pwd_hash:
                    login_win.destroy()
                    open_main_window(username)
                    return
        messagebox.showerror("Login Failed", "Invalid username or password.")

    def do_register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password to register.")
            return
        # check if user exists
        with open(USERS_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and row[0] == username:
                    messagebox.showinfo("Info", "Username already exists.")
                    return
        # add user
        with open(USERS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([username, hash_password(password)])
        messagebox.showinfo("Success", "Registration successful! You can now login.")

    tk.Button(login_win, text="Login", command=do_login, bg="lightgreen").pack(fill="x", padx=10, pady=(12, 4))
    tk.Button(login_win, text="Register", command=do_register, bg="lightblue").pack(fill="x", padx=10)
    tk.Label(login_win, text="(Passwords are securely hashed locally)", font=("Arial", 8)).pack(pady=(8,0))

    login_win.mainloop()

# ---------- Main App Window ----------
def open_main_window(username: str):
    global current_user, category_totals
    current_user = username
    category_totals = {}

    root = tk.Tk()
    root.title(f"Expense Tracker - {current_user}")
    root.geometry("400x650")

    # --- Functions (inner to access widgets) ---
    def update_category_menu():
        menu = category_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Select Category", command=lambda: category_var.set("Select Category"))
        for cat in CATEGORIES:
            menu.add_command(label=cat, command=lambda value=cat: category_var.set(value))

    def save_expense():
        amount = amount_entry.get().strip()
        category = category_var.get()
        note = note_entry.get().strip()

        if not amount or category == "Select Category":
            messagebox.showerror("Error", "Please fill amount and select category!")
            return

        try:
            # allow up to 2 decimals
            amount_val = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # write with username as 5th column
        with open(FILE_NAME, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date_time, f"{amount_val:.2f}", category, note, current_user])

        amount_entry.delete(0, tk.END)
        category_var.set("Select Category")
        note_entry.delete(0, tk.END)
        load_expenses(search_entry.get().strip())

    def load_expenses(search_text=""):
        # show only current user's expenses; if search_text provided, filter by category/note
        expenses_list.delete(0, tk.END)
        total = 0.0
        category_totals.clear()
        search_lower = search_text.strip().lower()

        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    # expect rows: datetime, amount, category, note, username
                    if not row:
                        continue
                    # handle legacy rows without username: skip them (or optionally treat as global)
                    if len(row) < 5:
                        continue
                    date_time, amount_str, category, note, username = row[:5]
                    if username != current_user:
                        continue
                    # apply search filter
                    if search_lower:
                        if search_lower not in category.lower() and search_lower not in note.lower():
                            continue
                    # show this row
                    try:
                        amount_val = float(amount_str)
                    except ValueError:
                        amount_val = 0.0
                    expenses_list.insert(tk.END, f"{date_time} | ₹{amount_val:.2f} | {category} ({note})")
                    total += amount_val
                    category_totals[category] = category_totals.get(category, 0.0) + amount_val

        total_label.config(text=f"Total: ₹{total:.2f}")

    def delete_expense():
        selected = expenses_list.curselection()
        if not selected:
            messagebox.showerror("Error", "Select an expense to delete!")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
        if not confirm:
            return

        index = selected[0]
        visible_items = expenses_list.get(0, tk.END)
        item_to_delete = visible_items[index]

        # read all expenses, remove matching one for current user and same string format
        if not os.path.exists(FILE_NAME):
            messagebox.showerror("Error", "No expense file found.")
            return

        with open(FILE_NAME, "r", newline="") as file:
            expenses = list(csv.reader(file))

        deleted = False
        for i, exp in enumerate(expenses):
            if not exp or len(exp) < 5:
                continue
            date_time, amount_str, category, note, username = exp[:5]
            if username != current_user:
                continue
            candidate = f"{date_time} | ₹{float(amount_str):.2f} | {category} ({note})"
            if candidate == item_to_delete:
                del expenses[i]
                deleted = True
                break

        if not deleted:
            messagebox.showerror("Error", "Could not find the selected expense in storage.")
            return

        with open(FILE_NAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(expenses)

        load_expenses(search_entry.get().strip())

    def show_category_totals():
        if not category_totals:
            messagebox.showinfo("Category Totals", "No expenses found!")
            return
        msg = "\n".join([f"{cat}: ₹{amt:.2f}" for cat, amt in category_totals.items()])
        messagebox.showinfo("Category Totals", msg)

    def search_expenses():
        load_expenses(search_entry.get().strip())

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

    def do_logout():
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if not confirm:
            return
        root.destroy()
        # return to login
        open_login_window()

    # --- UI layout ---
    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", pady=6, padx=6)

    tk.Label(top_frame, text=f"Logged in as: {current_user}", anchor="w").pack(side=tk.LEFT)
    tk.Button(top_frame, text="Logout", command=do_logout, bg="lightcoral").pack(side=tk.RIGHT)

    frame_input = tk.Frame(root)
    frame_input.pack(pady=5, fill="x", padx=6)

    tk.Label(frame_input, text="Amount (₹):").pack(anchor="w")
    amount_entry = tk.Entry(frame_input)
    amount_entry.pack(fill="x")

    tk.Label(frame_input, text="Category:").pack(anchor="w", pady=(6, 0))
    category_var = tk.StringVar(value="Select Category")
    category_menu = tk.OptionMenu(frame_input, category_var, *CATEGORIES)
    category_menu.pack(fill="x", pady=(0, 5))
    tk.Button(frame_input, text="Add New Category", command=add_category, bg="lightyellow").pack(fill="x", pady=(0, 5))

    tk.Label(frame_input, text="Note:").pack(anchor="w")
    note_entry = tk.Entry(frame_input)
    note_entry.pack(fill="x")

    tk.Button(frame_input, text="Add Expense", command=save_expense, bg="lightgreen").pack(fill="x", pady=8)

    frame_search = tk.Frame(root)
    frame_search.pack(pady=5, fill="x", padx=6)

    tk.Label(frame_search, text="Search:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(6, 6))
    tk.Button(frame_search, text="Go", command=search_expenses, bg="lightblue").pack(side=tk.LEFT)

    list_frame = tk.Frame(root)
    list_frame.pack(pady=5, fill="both", expand=True, padx=6)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    expenses_list = tk.Listbox(list_frame, width=60, height=16, yscrollcommand=scrollbar.set)
    expenses_list.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.config(command=expenses_list.yview)

    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=5)

    tk.Button(frame_buttons, text="Delete Selected", command=delete_expense, bg="tomato").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="Category Totals", command=show_category_totals, bg="orange").pack(side=tk.LEFT, padx=5)

    total_label = tk.Label(root, text="Total: ₹0.00", font=("Arial", 12, "bold"))
    total_label.pack(pady=5)

    update_category_menu()
    load_expenses()  # initial load for this user

    root.mainloop()

# Start the app
if __name__ == "__main__":
    open_login_window()
