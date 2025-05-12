
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import numpy as np
#
class FinanceManager:
    def __init__(self):
        self.transactions = []
        self.load_data()

    def export_data(self, filepath):
        with open(filepath, "w") as file:
            json.dump(self.transactions, file)

    def import_data(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                self.transactions = json.load(file)
            self.save_data()

    def add_transaction(self, type_, amount, category, date, description=""):
        transaction = {
            "type": type_,
            "amount": float(amount),
            "category": category,
            "date": date,
            "description": description
        }
        self.transactions.append(transaction)
        self.save_data()

    def delete_transaction(self, index):
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_data()

    def update_transaction(self, index, type_, amount, category, date, description=""):
        if 0 <= index < len(self.transactions):
            self.transactions[index] = {
                "type": type_,
                "amount": float(amount),
                "category": category,
                "date": date,
                "description": description
            }
            self.save_data()

    def filter_transactions(self, type_=None, category=None):
        return [
            t for t in self.transactions
            if (type_ is None or t["type"] == type_) and (category is None or t["category"] == category)
        ]

    def calculate_balance(self):
        income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        return income - expenses


    def summarize_transactions(self, period="Monthly", start_date=None, end_date=None):
        summary = {}
        filtered_transactions = [
            t for t in self.transactions
            if (start_date is None or t["date"] >= start_date) and (end_date is None or t["date"] <= end_date)
        ]
        date_key = None  # Initialize to prevent UnboundLocalError
        sorted_transactions = sorted(filtered_transactions, key=lambda t: t["date"])  # Ensure transactions are chronologically sorted
        for t in sorted_transactions:
            # TODO: normalize string by converting to lowercase
            if period == "Daily":
                date_key = t["date"][:10]
            elif period == "Monthly":
                date_key = t["date"][:7]
            elif period == "Yearly":
                date_key = t["date"][:4]
            elif period == "Weekly":
                year, week = int(t["date"][:4]), int(t["date"][5:7])
                date_key = f"{year}-W{week:02d}"  # Formats the week of the year
            elif period == "Decade":
                year = int(t["date"][:4])
                decade = year - (year % 10)
                date_key = f"{decade}s"
            else:
                raise ValueError("Invalid period specified")
            if date_key not in summary:
                summary[date_key] = {"income": 0, "expense": 0}
            summary[date_key][t["type"]] += t["amount"]
        summary = dict(sorted(summary.items()))  # Sort the summary dictionary by periods (keys)
        return summary

    def save_data(self):
        with open("data.json", "w") as file:
            json.dump(self.transactions, file)

    def load_data(self):
        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.transactions = json.load(file)
        else:
            self.transactions = []


class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.manager = FinanceManager()
        self.sort_descending = True  # Track sort order for amount column

        self.root.title("Personal Finance Manager")
        self.root.configure(bg="#f7f7f7")
        style = ttk.Style()
        style.configure("TLabel", background="#f7f7f7", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12))
        style.configure("Accent.TButton", font=("Arial", 14, "bold"), foreground="#000000", padding=10)
        style.map("Accent.TButton", background=[("active", "#0055A4"), ("!active", "#0078D7")])
        style.configure("Black.TLabelframe", background="#f7f7f7", font=("Arial", 14, "bold"))
        style.configure("TRadiobuttonLarge.TRadiobutton", font=("Arial", 14, "bold"))
        self.create_widgets()

    def sort_by_date(self):
        self.manager.transactions.sort(key=lambda t: t["date"], reverse=self.sort_descending)
        self.sort_descending = not self.sort_descending

        self.refresh_transactions()

    def sort_by_category(self):
        self.manager.transactions.sort(key=lambda t: t["category"], reverse=self.sort_descending)
        self.sort_descending = not self.sort_descending
        self.refresh_transactions()

    def sort_by_description(self):
        self.manager.transactions.sort(key=lambda t: t["description"], reverse=self.sort_descending)
        self.sort_descending = not self.sort_descending
        self.refresh_transactions()

    def create_widgets(self):
        # File Export/Import Section
        file_button_frame = ttk.Frame(self.root)
        file_button_frame.grid(row=11, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(file_button_frame, text="Export Data", command=self.export_data).pack(side="left", padx=5)
        ttk.Button(file_button_frame, text="Import Data", command=self.import_data).pack(side="right", padx=5)

        # Balance Section
        self.balance_label = ttk.Label(self.root, text=f"Current Balance: ${self.manager.calculate_balance():.2f}",
                                       font=("Arial", 14, "bold"), anchor="center")
        self.root.grid_columnconfigure(0, weight=1)  # Ensure column expands
        self.balance_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Add Transaction Section
        self.add_frame = ttk.LabelFrame(self.root, text="Add Transaction", style="Black.TLabelframe")
        self.root.grid_rowconfigure(1, weight=1)  # Allow the add_frame to expand vertically
        self.add_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.add_frame, text="Type:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.type_var = tk.StringVar(value="income")
        ttk.Radiobutton(self.add_frame, text="Income", variable=self.type_var, value="income",
                        style="TRadiobuttonLarge.TRadiobutton").grid(row=0, column=1, padx=5, sticky="w")
        ttk.Radiobutton(self.add_frame, text="Expense", variable=self.type_var, value="expense",
                        style="TRadiobuttonLarge.TRadiobutton").grid(row=0, column=2, padx=5, sticky="w")

        ttk.Label(self.add_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5)
        self.amount_entry = ttk.Entry(self.add_frame, font=("Arial", 12))
        self.amount_entry.grid(row=1, column=1)

        ttk.Label(self.add_frame, text="Category:").grid(row=2, column=0, sticky="w", padx=5)
        self.category_entry = ttk.Entry(self.add_frame)
        self.category_entry.grid(row=2, column=1)

        ttk.Label(self.add_frame, text="Date:").grid(row=3, column=0, sticky="w", padx=5)
        self.date_entry = DateEntry(self.add_frame, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=3, column=1)

        ttk.Label(self.add_frame, text="Description:").grid(row=4, column=0, sticky="w", padx=5)
        self.description_entry = ttk.Entry(self.add_frame)
        self.description_entry.grid(row=4, column=1)

        ttk.Button(self.add_frame, text="Add", command=self.add_transaction, style="Accent.TButton").grid(row=5,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          padx=5,
                                                                                                          pady=10)
        self.root.bind("<Return>", lambda event: self.add_transaction())

        # Transaction List Section
        self.transactions_frame = ttk.LabelFrame(self.root, text="Transactions")
        self.root.grid_rowconfigure(2, weight=3)  # Allow transactions_frame to expand vertically
        self.transactions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.transactions_frame.grid_columnconfigure(0, weight=1)

        # Frame for Treeview and Scrollbars
        treeview_container = ttk.Frame(self.transactions_frame)
        treeview_container.grid(row=0, column=0, sticky="nsew")
        self.transactions_frame.grid_rowconfigure(0, weight=1)
        self.transactions_frame.grid_columnconfigure(0, weight=1)

        self.transactions_tree = ttk.Treeview(treeview_container,
                                              columns=("Type", "Amount", "Category", "Date", "Description"),
                                              show="headings", style="primary.Treeview")
        self.transactions_tree.tag_configure("oddrow", background="#f0f0f0")
        self.transactions_tree.tag_configure("evenrow", background="#ffffff")
        self.transactions_tree.heading("Type", text="Type", command=self.sort_by_type)
        self.transactions_tree.heading("Amount", text="Amount", command=self.sort_by_amount)
        self.transactions_tree.heading("Category", text="Category", command=self.sort_by_category)
        self.transactions_tree.heading("Date", text="Date", command=self.sort_by_date)
        self.transactions_tree.heading("Description", text="Description", command=self.sort_by_description)
        self.transactions_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Scrollbars for Treeview
        scroll_y = ttk.Scrollbar(treeview_container, orient="vertical", command=self.transactions_tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x = ttk.Scrollbar(treeview_container, orient="horizontal", command=self.transactions_tree.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.transactions_tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        # Buttons below the Treeview
        button_frame = ttk.Frame(self.transactions_frame)
        button_frame.grid(row=1, column=0, sticky="ew")  # Positioned below the treeview
        ttk.Button(button_frame, text="Delete", command=self.delete_transaction).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Update", command=self.update_transaction).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_transactions).pack(side="left", padx=5, pady=5)
        self.root.bind("<Delete>", lambda event: self.delete_transaction())
        self.root.bind("<Tab>", lambda event: self.update_transaction())

        # Bind double-click event to populate fields
        self.transactions_tree.bind("<Double-1>", self.populate_fields)

        # Graph Options Section
        self.graph_type_var = tk.StringVar(value="Bar Chart")
        self.graph_type_dropdown = ttk.Combobox(self.root, textvariable=self.graph_type_var,
                                                values=["Bar Chart", "Line Chart", "Pie Chart", "Category (Bar Chart)",
                                                        "Category (Line Chart)", "Category (Pie Charts)"],
                                                state="readonly",
                                                font=("Arial", 12))
        self.graph_type_dropdown.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        ttk.Label(self.root, text="Time Interval:", font=("Arial", 14)).grid(row=5, column=0, sticky="w", padx=10,
                                                                             pady=5)
        self.time_period_var = tk.StringVar(value="Monthly")
        self.time_period_dropdown = ttk.Combobox(self.root, textvariable=self.time_period_var,
                                                 values=["Daily", "Weekly", "Monthly", "Yearly", "Decade"],
                                                 state="readonly", font=("Arial", 12))
        self.time_period_dropdown.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Start Date:", font=("Arial", 14)).grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.start_date_entry = DateEntry(self.root, date_pattern="yyyy-mm-dd", selectmode="day", font=("Arial", 12))
        self.start_date_entry.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="End Date:", font=("Arial", 14)).grid(row=9, column=0, sticky="w", padx=10, pady=5)
        self.end_date_entry = DateEntry(self.root, date_pattern="yyyy-mm-dd", selectmode="day", font=("Arial", 12))
        self.end_date_entry.grid(row=10, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(self.root, text="Show Graph", command=self.show_graph, style="Accent.TButton").grid(row=4, column=0,
                                                                                                       padx=20, pady=10,
                                                                                                       sticky="ew")

        self.refresh_transactions()


    def add_transaction(self):
        type_ = self.type_var.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()
        description = self.description_entry.get()

        if amount.replace('.', '', 1).isdigit() and date and category:  # Allows decimals for amounts
            self.manager.add_transaction(type_, amount, category, date, description)
            self.refresh_transactions()
            self.balance_label.config(text=f"Current Balance: ${self.manager.calculate_balance():.2f}")
            msg_box = messagebox.showinfo("Success", "Transaction added successfully!")

        else:
            msg_box = messagebox.showerror("Error", "Please enter valid data!")


    def delete_transaction(self):
        selected_items = self.transactions_tree.selection()
        if selected_items:
            indices = [self.transactions_tree.index(item) for item in selected_items]
            for index in sorted(indices, reverse=True):  # Reverse to avoid index shifting
                self.manager.delete_transaction(index)
            self.refresh_transactions()
            self.balance_label.config(text=f"Current Balance: ${self.manager.calculate_balance():.2f}")
            msg_box = messagebox.showinfo("Success", f"{len(selected_items)} transactions deleted successfully!")

        else:
            msg_box = messagebox.showerror("Error", "Please select one or more transactions to delete!")

    def update_transaction(self):
        selected_items = self.transactions_tree.selection()
        if selected_items:
            for item in selected_items:
                index = self.transactions_tree.index(item)
                type_ = self.type_var.get()
                amount = self.amount_entry.get()
                category = self.category_entry.get()
                date = self.date_entry.get()
                description = self.description_entry.get()

                if amount.replace('.', '', 1).isdigit() and date and category:
                    self.manager.update_transaction(index, type_, amount, category, date, description)
                else:
                    msg_box = messagebox.showerror("Error", "Please enter valid data and try again!")

                    return
            self.refresh_transactions()
            self.balance_label.config(text=f"Current Balance: ${self.manager.calculate_balance():.2f}")
            msg_box = messagebox.showinfo("Success", "Selected transactions updated successfully!")

        else:
            messagebox.showerror("Error", "Please select one or more transactions to update!")

    def clear_transactions(self):
        self.manager.transactions.clear()  # Clear the transactions list
        self.manager.save_data()  # Save the empty state
        self.refresh_transactions()
        self.balance_label.config(text=f"Current Balance: ${self.manager.calculate_balance():.2f}")
        messagebox.showinfo("Success", "All transactions have been cleared!")

    def sort_by_type(self):
        self.manager.transactions.sort(key=lambda t: t["type"] == "expense" and 1 or 0, reverse=self.sort_descending)
        self.sort_descending = not self.sort_descending
        self.refresh_transactions()

    def refresh_transactions(self):
        for i in self.transactions_tree.get_children():
            self.transactions_tree.delete(i)

        for idx, t in enumerate(self.manager.transactions):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.transactions_tree.insert("", "end", values=(
                t["type"].capitalize(), f"${t['amount']:.2f}", t["category"], t["date"], t["description"]), tags=(tag,))

    def sort_by_amount(self):
        self.manager.transactions.sort(key=lambda t: t["amount"], reverse=self.sort_descending)
        self.sort_descending = not self.sort_descending
        self.refresh_transactions()

    def group_transactions_by_category(self, transactions):
        categories = {}
        for t in transactions:
            cat = t["category"]
            if cat not in categories:
                categories[cat] = {"income": 0, "expense": 0}
            categories[cat][t["type"]] += t["amount"]
        return dict(sorted(categories.items()))  # Sort categories alphabetically

    def show_graph(self):
        time_period = self.time_period_var.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        graph_type = self.graph_type_var.get()
        filtered_transactions = [
            t for t in self.manager.transactions if start_date <= t["date"] <= end_date
        ]

        if graph_type in ["Category (Bar Chart)", "Category (Line Chart)", "Category (Pie Charts)"]:
            category_summary = self.group_transactions_by_category(filtered_transactions)
            categories = list(category_summary.keys())
            incomes = [category_summary[cat]["income"] for cat in categories]
            expenses = [category_summary[cat]["expense"] for cat in categories]

            plt.figure(figsize=(10, 6))
            if graph_type == "Category (Bar Chart)":
                x_pos = np.arange(len(categories))
                plt.bar(x_pos - 0.2, incomes, 0.4, label="Income", color="green")
                plt.bar(x_pos + 0.2, expenses, 0.4, label="Expense", color="red")
                plt.xticks(x_pos, categories, rotation=45)
                plt.xlabel("Category")
                plt.ylabel("Amount")
                plt.title("Transactions by Category")
                plt.legend()
            elif graph_type == "Category (Line Chart)":
                plt.plot(categories, incomes, marker="o", label="Income", color="green")
                plt.plot(categories, expenses, marker="o", label="Expense", color="red")
                plt.xlabel("Category")
                plt.ylabel("Amount")
                plt.title("Transactions by Category")
                plt.legend()
                plt.xticks(rotation=45)
            elif graph_type == "Category (Pie Charts)":
                fig, ax = plt.subplots(1, 2, figsize=(12, 6))
                ax[0].pie(incomes, labels=categories, autopct="%1.1f%%", colors=plt.cm.Paired.colors[:len(categories)])
                ax[0].set_title("Income by Category")
                ax[1].pie(expenses, labels=categories, autopct="%1.1f%%", colors=plt.cm.Paired.colors[:len(categories)])
                ax[1].set_title("Expenses by Category")
            plt.tight_layout()
            plt.show()

        else:
            summary = self.manager.summarize_transactions(period=time_period, start_date=start_date, end_date=end_date)
            periods = list(summary.keys())
            incomes = [summary[period]["income"] for period in periods]
            expenses = [summary[period]["expense"] for period in periods]

            plt.figure(figsize=(10, 6))
            if graph_type == "Bar Chart":
                plt.bar(periods, incomes, color="green", label="Income")
                plt.bar(periods, expenses, color="red", label="Expenses", bottom=incomes)
            elif graph_type == "Line Chart":
                plt.plot(periods, incomes, color="green", marker="o", label="Income")
                plt.plot(periods, expenses, color="red", marker="o", label="Expenses")
            elif graph_type == "Pie Chart":
                total_income = sum(incomes)
                total_expenses = sum(expenses)
                plt.pie([total_income, total_expenses], labels=["Income", "Expenses"], autopct="%1.1f%%", colors=["green", "red"])

            if graph_type != "Pie Chart":
                plt.xlabel("Period")
                plt.ylabel("Amount")
                plt.title("Income and Expenses Summary")
                plt.legend()
                plt.xticks(rotation=45)

            plt.tight_layout()
            plt.show()

    def handle_delete_key(self):
        """Handles the Delete key press to remove the selected transactions."""
        self.delete_transaction()

    def export_data(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Export Data"
        )
        if filepath:
            self.manager.export_data(filepath)
            msg_box = messagebox.showinfo("Success", "Data exported successfully!")


    def import_data(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Import Data"
        )
        if filepath:
            self.manager.import_data(filepath)
            self.refresh_transactions()
            self.balance_label.config(text=f"Current Balance: ${self.manager.calculate_balance():.2f}")
            msg_box = messagebox.showinfo("Success", "Data imported successfully!")


    def populate_fields(self, event):
        selected_item = self.transactions_tree.selection()
        if selected_item:
            data = self.transactions_tree.item(selected_item, "values")
            self.type_var.set(data[0].lower())  # Ensure correct format for type_var
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, data[1][1:])
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, data[2])
            self.date_entry.set_date(data[3])
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, data[4])




if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()