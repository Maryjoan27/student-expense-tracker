import tkinter as tk
from tkinter import messagebox
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "data/expenses.csv"

# Ensure CSV exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date","amount","category","description","payment_method"])


def save_expense():

    date = date_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    payment = payment_entry.get()

    if date == "" or amount == "":
        messagebox.showerror("Error", "Date and Amount are required")
        return

    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([date, amount, category, description, payment])

    messagebox.showinfo("Success", "Expense saved successfully!")

    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    payment_entry.delete(0, tk.END)

def show_chart():

    if not os.path.exists(DATA_FILE):
        messagebox.showerror("Error", "No data available")
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        messagebox.showerror("Error", "No expenses recorded")
        return

    category_total = df.groupby("category")["amount"].sum()

    category_total.plot(kind="bar")

    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₦)")
    plt.show()

# GUI Window
root = tk.Tk()
root.title("Student Expense Tracker")
root.geometry("400x350")

# Date
tk.Label(root, text="Date (YYYY-MM-DD)").pack()
date_entry = tk.Entry(root)
date_entry.pack()

# Amount
tk.Label(root, text="Amount").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

# Category
tk.Label(root, text="Category").pack()
category_entry = tk.Entry(root)
category_entry.pack()

# Description
tk.Label(root, text="Description").pack()
description_entry = tk.Entry(root)
description_entry.pack()

# Payment
tk.Label(root, text="Payment Method").pack()
payment_entry = tk.Entry(root)
payment_entry.pack()

# Save Button
save_button = tk.Button(root, text="Save Expense", command=save_expense)
save_button.pack(pady=10)

chart_button = tk.Button(root, text="Show Spending Chart", command=show_chart)
chart_button.pack(pady=10)

root.mainloop()