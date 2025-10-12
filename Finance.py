import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import uuid
from tkinter import font

class FinanceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager")
        self.data_file = "finance_data.json"
        self.categories = {"children": {}, "type": "Virtual", "balance": 0.0, "transactions": []}
        # Initialize style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", highlightthickness=0)
        self.style.configure("Treeview.Heading", relief="flat")
        self.style.configure("Narrow.Vertical.TScrollbar", width=12)  # Narrow scrollbar
        self.load_data()

        # Configure root window
        self.root.geometry("1000x600")  # Set initial size
        self.root.maxsize(1000, 600)    # Set max size equal to initial size
        self.root.resizable(False, False)  # Disable resizing and maximization
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # GUI Components
        self.create_gui()
        self.transaction_tree = None  # Initialize here to persist

    def load_data(self):
        """Load data from JSON file, handle errors, and ensure balance keys."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                if not isinstance(loaded_data, dict):
                    raise ValueError("JSON root must be a dictionary")
                self.categories = loaded_data
                self.ensure_balance_keys(self.categories)
            else:
                self.save_data()
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Corrupted JSON file: {str(e)}. Starting with empty data.")
            self.categories = {"children": {}, "type": "Virtual", "balance": 0.0, "transactions": []}
            self.save_data()

    def ensure_balance_keys(self, category):
        """Recursively ensure every category has required keys and correct structure."""
        if "balance" not in category:
            category["balance"] = 0.0
        if "type" not in category:
            category["type"] = "Virtual"
        if "transactions" not in category:
            category["transactions"] = []
        if "children" not in category or not isinstance(category["children"], dict):
            category["children"] = {}
        if category["type"] == "Cash" and "denominations" not in category:
            category["denominations"] = {
                "bills": {"500": 0, "200": 0, "100": 0, "50": 0, "20": 0, "10": 0, "5": 0},
                "coins": {"2": 0, "1": 0, "0.5": 0, "0.2": 0, "0.1": 0}
            }
        for child in category["children"].values():
            self.ensure_balance_keys(child)

    def save_data(self):
        """Save data to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.categories, f, indent=4)

    def calculate_total_balance(self, category=None):
        """Calculate total balance of all categories recursively."""
        if category is None:
            category = self.categories
        return self.calculate_balance(category)

    def calculate_balance(self, category):
        if category["type"] == "Summary":
            balance = sum(self.calculate_balance(child) for child in category["children"].values())
            print(f"Summary {category.get('type', 'Unknown')} balance: {balance:.2f} from {len(category['children'])} children")
            return balance
        balance = category["balance"]
        for child in category["children"].values():
            balance += self.calculate_balance(child)
        if category["type"] == "Cash":
            cash_balance = sum(int(k) * v for k, v in category["denominations"]["bills"].items()) + \
                          sum(float(k) * v for k, v in category["denominations"]["coins"].items())
            category["balance"] = cash_balance
            balance = cash_balance
        return balance

    def create_gui(self):
        """Set up the optimized GUI layout."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(0, weight=0)  # Toolbar fixed height
        self.main_frame.grid_rowconfigure(1, weight=1)  # Other content expands
        self.main_frame.grid_columnconfigure(0, weight=1)  # Treeview section
        self.main_frame.grid_columnconfigure(1, weight=0)  # Spacer
        self.main_frame.grid_columnconfigure(2, weight=2)  # Details/Actions section

        # Toolbar for buttons
        toolbar = ttk.Frame(self.main_frame)
        toolbar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar.grid_rowconfigure(0, minsize=40)  # Ensure toolbar has minimum height

        buttons = [
            ("Add Category", self.show_add_category_form, "Create a new category or subcategory"),
            ("Rename Category", self.show_rename_category_form, "Rename the selected category"),
            ("Delete Category", self.show_delete_category_form, "Delete the selected category and its subcategories"),
            ("Add Transaction", self.show_add_transaction_form, "Add a transaction to a Virtual category"),
            ("View Full Transaction History", self.show_transaction_history_from_toolbar, "View all transactions for the selected category")
        ]
        self.history_button = ttk.Button(toolbar, text="View Full Transaction History", command=self.show_transaction_history_from_toolbar, state="disabled")
        self.history_button.grid(row=0, column=4, padx=5)
        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ttk.Button(toolbar, text=text, command=command)
            btn.grid(row=0, column=i, padx=5)
            btn.bind('<Enter>', lambda e, t=tooltip: self.show_tooltip(e, t))
            btn.bind('<Leave>', self.hide_tooltip)

        # Category Treeview with scrollbar
        tree_frame = ttk.LabelFrame(self.main_frame, text="Categories", padding="5")
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 5))  # Fixed width section
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.configure(width=333)  # One-third of 1000px

        self.tree = ttk.Treeview(tree_frame, columns=("Balance",), selectmode="browse", height=20)
        self.tree.heading("#0", text="Category")
        self.tree.heading("Balance", text="Balance (€)", anchor="w")  # Left-aligned header
        self.tree.column("Balance", width=133, minwidth=133, anchor="w")  # Left-aligned content
        self.tree.column("#0", width=200, minwidth=200, stretch=True)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Right side: Details (top) and Actions (bottom)
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(5, 0))
        self.right_frame.grid_rowconfigure(0, weight=1)  # Details expands
        self.right_frame.grid_rowconfigure(1, weight=0)  # Actions fixed height
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Details frame with minimum height
        self.detail_frame = ttk.LabelFrame(self.right_frame, text="Details", padding="15")
        self.detail_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), pady=(0, 15))
        self.detail_frame.grid_rowconfigure(0, weight=1)
        self.detail_frame.grid_rowconfigure(0, minsize=200)  # Minimum height to preserve border
        self.detail_content = ttk.Frame(self.detail_frame)
        self.detail_content.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.detail_content.grid_columnconfigure(0, weight=1)

        self.actions_frame = ttk.LabelFrame(self.right_frame, text="Actions", padding="10")
        self.actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.S), pady=(10, 0))
        self.actions_frame.grid_rowconfigure(0, minsize=150)  # Minimum height
        self.actions_content = ttk.Frame(self.actions_frame)
        self.actions_content.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.actions_content.grid_rowconfigure(0, weight=1)
        self.actions_content.grid_rowconfigure(1, weight=1)
        self.actions_content.grid_columnconfigure(0, weight=1)
        self.actions_content.grid_columnconfigure(1, weight=1)

        # Status bar for total balance
        self.status_frame = ttk.Frame(self.root, style="Status.TFrame")
        self.style.configure("Status.TFrame", background="#f0f0f0")
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.status_label = ttk.Label(
            self.status_frame,
            text="Total Balance: €0.00",
            font=("TkDefaultFont", 14, "bold"),
            background="#f0f0f0",
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.root.grid_rowconfigure(1, weight=0)

        self.populate_tree()
        self.update_total_balance()

        # Tooltip
        self.tooltip = None

        # Start with empty actions
        self.clear_actions()

    def update_total_balance(self):
        """Update the total balance display."""
        total = self.calculate_total_balance()
        self.status_label.config(text=f"Total Balance: €{total:.2f}")

    def show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.destroy()
        x, y = event.widget.winfo_rootx() + 20, event.widget.winfo_rooty() + 20
        self.tooltip = tk.Label(self.root, text=text, background="yellow", relief="solid", borderwidth=1)
        self.tooltip.place(x=x, y=y)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def clear_actions(self):
        widget_count = len(self.actions_content.winfo_children())
        print(f"Clearing {widget_count} widgets from actions_content")
        for widget in self.actions_content.winfo_children():
            widget.destroy()
        self.actions_content.destroy()
        self.actions_content = ttk.Frame(self.actions_frame)
        self.actions_content.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.actions_content.grid_rowconfigure(0, weight=1)
        self.actions_content.grid_rowconfigure(1, weight=1)
        self.actions_content.grid_columnconfigure(0, weight=1)
        self.actions_content.grid_columnconfigure(1, weight=1)
        print(f"After clearing, {len(self.actions_content.winfo_children())} widgets remain")

    def populate_tree(self, parent="", category=None, path=""):
        if category is None:
            category = self.categories
        selected_iid = self.tree.selection()  # Store current selection
        selected_path = self.get_selected_path(silent=True) if selected_iid else None
        self.tree.delete(*self.tree.get_children(parent))
        for name, data in sorted(category["children"].items()):
            full_path = f"{path}.{name}" if path else name
            balance = self.calculate_balance(data)
            # Ensure balance text is cleanly formatted and left-aligned
            balance_str = f"{balance:.2f}".rstrip('0').rstrip('.') if balance.is_integer() else f"{balance:.2f}"
            iid = self.tree.insert(parent, "end", text=f"{name} ({data['type']})", values=(balance_str,), tags=(full_path,))
            self.populate_tree(iid, data, full_path)
        self.update_total_balance()
        # Restore selection if possible
        if selected_path:
            try:
                parts = selected_path.split(".")
                current_iid = ""
                for part in parts:
                    for child in self.tree.get_children(current_iid):
                        if self.tree.item(child)["text"].split(" (")[0] == part:
                            current_iid = child
                            break
                    if not current_iid:
                        break
                if current_iid:
                    self.tree.selection_set(current_iid)
                    self.tree.see(current_iid)
            except tk.TclError:
                pass
        elif self.tree.get_children():
            self.tree.selection_set(self.tree.get_children()[0])
            self.tree.see(self.tree.get_children()[0])

    def get_category(self, path):
        if not path:
            return self.categories
        parts = path.split(".")
        current = self.categories
        for part in parts:
            if part not in current["children"]:
                raise KeyError(f"Category '{part}' not found in path '{path}'")
            current = current["children"][part]
        return current

    def get_selected_path(self, silent=False):
        selected = self.tree.selection()
        if not selected:
            if not silent:
                messagebox.showwarning("Warning", "Please select a category first.")
            return None
        item = self.tree.item(selected[0])
        path_parts = []
        current_iid = selected[0]
        while current_iid:
            item_text = self.tree.item(current_iid)["text"].split(" (")[0]
            path_parts.insert(0, item_text)
            current_iid = self.tree.parent(current_iid)
        full_path = ".".join(path_parts)
        try:
            self.get_category(full_path)
            return full_path
        except KeyError as e:
            if not silent:
                messagebox.showerror("Error", f"Invalid category path: {full_path}. {str(e)}")
            return None

    def show_add_category_form(self):
        self.clear_actions()
        row = 0
        ttk.Label(self.actions_content, text="Category Name:", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(self.actions_content, width=20)
        name_entry.grid(row=row, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        row += 1

        ttk.Label(self.actions_content, text="Category Type:", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        type_var = tk.StringVar(value="Virtual")
        ttk.Radiobutton(self.actions_content, text="Virtual", variable=type_var, value="Virtual").grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Radiobutton(self.actions_content, text="Cash", variable=type_var, value="Cash").grid(row=row, column=2, sticky=tk.W, padx=10)
        ttk.Radiobutton(self.actions_content, text="Summary", variable=type_var, value="Summary").grid(row=row, column=3, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(self.actions_content, text="Root or Subcategory:", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        level_var = tk.StringVar(value="Root")
        ttk.Radiobutton(self.actions_content, text="Root", variable=level_var, value="Root").grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Radiobutton(self.actions_content, text="Subcategory", variable=level_var, value="Sub").grid(row=row, column=2, sticky=tk.W, padx=10)
        row += 1

        def submit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Category name cannot be empty.")
                return
            try:
                parent_path = self.get_selected_path(silent=True) if level_var.get() == "Sub" else ""
                if level_var.get() == "Sub" and not parent_path:
                    return
                parent = self.get_category(parent_path) if parent_path else self.categories
                if name in parent["children"]:
                    messagebox.showerror("Error", f"Category '{name}' already exists in the parent.")
                    return
                new_category = {
                    "children": {},
                    "type": type_var.get(),
                    "balance": 0.0 if type_var.get() != "Summary" else 0.0,
                    "transactions": []
                }
                if type_var.get() == "Cash":
                    new_category["denominations"] = {
                        "bills": {"500": 0, "200": 0, "100": 0, "50": 0, "20": 0, "10": 0, "5": 0},
                        "coins": {"2": 0, "1": 0, "0.5": 0, "0.2": 0, "0.1": 0}
                    }
                elif type_var.get() == "Summary":
                    new_category.pop("balance", None)
                    new_category.pop("transactions", None)
                parent["children"][name] = new_category
                self.save_data()
                self.populate_tree()
                name_entry.delete(0, tk.END)
                self.update_history_button_state()
            except KeyError as e:
                messagebox.showerror("Error", f"Invalid parent category: {str(e)}")

        ttk.Button(self.actions_content, text="Add", command=submit).grid(row=row, column=0, columnspan=2, pady=5, padx=10)
        ttk.Button(self.actions_content, text="Close", command=self.clear_actions).grid(row=row, column=2, columnspan=2, pady=5, padx=10)
        row += 1
        ttk.Label(self.actions_content, text="(Creates a new category or subcategory)", wraplength=300).grid(row=row, column=0, columnspan=4, pady=5, sticky="nsew")

    def show_rename_category_form(self):
        self.clear_actions()
        path = self.get_selected_path()
        if not path:
            return
        row = 0
        parent_path = ""
        old_name = path
        if "." in path:
            parent_path, old_name = path.rsplit(".", 1)
        try:
            parent = self.get_category(parent_path) if parent_path else self.categories
        except KeyError:
            messagebox.showerror("Error", f"Parent category not found for '{path}'")
            return

        ttk.Label(self.actions_content, text=f"Rename '{path}' to:", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky="nsew")
        name_entry = ttk.Entry(self.actions_content, width=20)
        name_entry.grid(row=row, column=1, padx=10, pady=5, sticky="nsew")
        name_entry.insert(0, old_name)
        row += 1

        def submit():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Category name cannot be empty.")
                return
            if new_name in parent["children"]:
                messagebox.showerror("Error", f"Category '{new_name}' already exists in the parent.")
                return
            try:
                parent["children"][new_name] = parent["children"].pop(old_name)
                self.save_data()
                self.populate_tree()
                name_entry.delete(0, tk.END)
                name_entry.insert(0, new_name)
                self.update_history_button_state()
            except KeyError:
                messagebox.showerror("Error", "Error renaming category.")

        ttk.Button(self.actions_content, text="Rename", command=submit).grid(row=row, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")
        ttk.Button(self.actions_content, text="Close", command=self.clear_actions).grid(row=row, column=2, columnspan=2, pady=5, padx=10, sticky="nsew")
        row += 1
        ttk.Label(self.actions_content, text="(Renames the selected category)", wraplength=300).grid(row=row, column=0, columnspan=4, pady=5, sticky="nsew")

    def show_delete_category_form(self):
        self.clear_actions()
        path = self.get_selected_path(silent=True)
        if not path:
            return
        row = 0
        ttk.Label(self.actions_content, text=f"Confirm delete '{path}' and subcategories?", wraplength=300).grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        def submit():
            parent_path = ""
            name = path
            if "." in path:
                parent_path, name = path.rsplit(".", 1)
            try:
                parent = self.get_category(parent_path) if parent_path else self.categories
                if name not in parent["children"]:
                    messagebox.showerror("Error", f"Category '{name}' not found in the parent.")
                    return
                del parent["children"][name]
                self.save_data()
                self.populate_tree()
                self.clear_detail_frame()
                self.clear_actions()
                self.update_history_button_state()
                if self.tree.get_children():
                    self.tree.selection_set(self.tree.get_children()[0])
                    self.on_tree_select(None)
            except KeyError as e:
                messagebox.showerror("Error", f"Error deleting category '{path}': {str(e)}")

        ttk.Button(self.actions_content, text="Delete", command=submit).grid(row=row + 1, column=0, pady=5, padx=10, sticky="nsew")
        ttk.Button(self.actions_content, text="Cancel", command=self.clear_actions).grid(row=row + 1, column=1, pady=5, padx=10, sticky="nsew")
        row += 2
        ttk.Label(self.actions_content, text="(Deletes the selected category and its subcategories)", wraplength=300).grid(row=row, column=0, columnspan=2, pady=5, sticky="nsew")

    def show_add_transaction_form(self):
        self.clear_actions()
        row = 0
        ttk.Label(self.actions_content, text="Amount (€):", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky="nsew")
        amount_entry = ttk.Entry(self.actions_content, width=20)
        amount_entry.grid(row=row, column=1, padx=10, pady=5, sticky="nsew")
        row += 1

        ttk.Label(self.actions_content, text="Description:", wraplength=300).grid(row=row, column=0, padx=10, pady=5, sticky="nsew")
        desc_entry = ttk.Entry(self.actions_content, width=20)
        desc_entry.grid(row=row, column=1, padx=10, pady=5, sticky="nsew")
        row += 1

        def submit():
            path = self.get_selected_path()
            if not path:
                return
            try:
                category = self.get_category(path)
                if category["type"] != "Virtual":
                    messagebox.showerror("Error", "Transactions can only be added to Virtual categories.")
                    return
                amount = float(amount_entry.get())
                desc = desc_entry.get().strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                category["transactions"].append({
                    "id": str(uuid.uuid4()),
                    "amount": amount,
                    "description": desc,
                    "timestamp": timestamp
                })
                category["balance"] += amount
                self.save_data()
                self.populate_tree()
                amount_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                self.on_tree_select(None)
                self.update_history_button_state()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount. Enter a number (e.g., 10.50).")

        ttk.Button(self.actions_content, text="Add Transaction", command=submit).grid(row=row, column=0, columnspan=2, pady=5, padx=10)
        ttk.Button(self.actions_content, text="Close", command=self.clear_actions).grid(row=row, column=2, columnspan=2, pady=5, padx=10)
        row += 1
        ttk.Label(self.actions_content, text="(Adds a transaction to a Virtual category)", wraplength=300).grid(row=row, column=0, columnspan=4, pady=5, sticky="nsew")

    def on_tree_select(self, event):
        self.clear_detail_frame()
        selected = self.tree.selection()
        if not selected:
            return
        path = self.get_selected_path()
        if not path:
            return
        try:
            category = self.get_category(path)
            if category["type"] == "Cash":
                self.show_cash_details(category)
            elif category["type"] == "Summary":
                self.show_summary_details(category)
            else:
                self.show_transaction_details(category)
            self.update_history_button_state()
        except KeyError:
            messagebox.showerror("Error", f"Cannot load details for '{path}'.")

    def clear_detail_frame(self):
        for widget in self.detail_content.winfo_children():
            widget.destroy()

    def show_cash_details(self, category):
        canvas = tk.Canvas(self.detail_content)
        v_scrollbar = ttk.Scrollbar(self.detail_content, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.detail_content.grid_rowconfigure(0, weight=1)
        self.detail_content.grid_columnconfigure(0, weight=1)

        ttk.Label(scrollable_frame, text="Bills (€):", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        bill_entries = {}
        row = 1
        for denom in sorted(category["denominations"]["bills"].keys(), key=int, reverse=True):
            ttk.Label(scrollable_frame, text=f"{denom} €").grid(row=row, column=0, padx=5, sticky=tk.W)
            entry = ttk.Entry(scrollable_frame, width=10)
            entry.insert(0, str(category["denominations"]["bills"][denom]))
            entry.grid(row=row, column=1, padx=5, pady=2)
            bill_entries[denom] = entry
            row += 1

        ttk.Label(scrollable_frame, text="Coins (€):", font=("TkDefaultFont", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W)
        row += 1
        coin_entries = {}
        for denom in sorted(category["denominations"]["coins"].keys(), key=float, reverse=True):
            ttk.Label(scrollable_frame, text=f"{denom} €").grid(row=row, column=0, padx=5, sticky=tk.W)
            entry = ttk.Entry(scrollable_frame, width=10)
            entry.insert(0, str(category["denominations"]["coins"][denom]))
            entry.grid(row=row, column=1, padx=5, pady=2)
            coin_entries[denom] = entry
            row += 1

        def save_denominations():
            try:
                for denom, entry in bill_entries.items():
                    value = entry.get().strip()
                    if not value.isdigit():
                        raise ValueError(f"Invalid count for {denom} € bill.")
                    category["denominations"]["bills"][denom] = int(value)
                for denom, entry in coin_entries.items():
                    value = entry.get().strip()
                    if not value.isdigit():
                        raise ValueError(f"Invalid count for {denom} € coin.")
                    category["denominations"]["coins"][denom] = int(value)
                self.save_data()
                self.populate_tree()
                self.on_tree_select(None)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(scrollable_frame, text="Save Denominations", command=save_denominations).grid(row=row, column=0, columnspan=2, pady=10)

    def show_transaction_details(self, category):
        # Ensure transaction_tree is created and managed
        if self.transaction_tree is None:
            main_frame = ttk.Frame(self.detail_content, padding="5")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            main_frame.grid_rowconfigure(0, weight=0)  # Treeview fixed height
            main_frame.grid_rowconfigure(1, weight=1)  # Extra space
            main_frame.grid_columnconfigure(0, weight=1)
            self.transaction_tree = ttk.Treeview(main_frame, columns=("Date", "Amount", "Description"), selectmode="none", height=10)
            self.transaction_tree.heading("Date", text="Date")
            self.transaction_tree.heading("Amount", text="Amount (€)")
            self.transaction_tree.heading("Description", text="Description")
            self.transaction_tree.column("#0", width=0, stretch=False, minwidth=0)
            self.transaction_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif self.transaction_tree.winfo_exists() == 0:
            self.transaction_tree = None  # Reset if destroyed
            return self.show_transaction_details(category)  # Recreate

        # Defer width calculation to ensure layout is ready
        def set_columns():
            if self.transaction_tree.winfo_exists():
                self.root.update_idletasks()
                detail_width = self.detail_content.winfo_width() or 600
                padding = 20
                available_width = detail_width - padding
                min_total_width = 150 + 100 + 300
                if available_width > min_total_width:
                    extra_width = available_width - min_total_width
                    desc_width = 300 + extra_width
                else:
                    desc_width = 300

                self.transaction_tree.column("Date", width=150, minwidth=150, stretch=False, anchor="center")
                self.transaction_tree.column("Amount", width=100, minwidth=100, stretch=False, anchor="center")
                self.transaction_tree.column("Description", width=int(desc_width), minwidth=300, stretch=False, anchor="w")
                populate_tree(detail_width, desc_width)
            else:
                print("Transaction tree no longer exists, skipping update")

        def populate_tree(detail_width, desc_width):
            if self.transaction_tree.winfo_exists():
                self.transaction_tree.delete(*self.transaction_tree.get_children())
                transactions = sorted(category["transactions"], key=lambda x: x.get("timestamp", ""), reverse=True)
                for trans in transactions[:10]:
                    self.transaction_tree.insert("", "end", values=(
                        trans.get("timestamp", "N/A"),
                        f"{trans.get('amount', 0.0):.2f}",
                        trans.get("description", "(No description)")
                    ))
                self.root.update_idletasks()
                tree_height = self.transaction_tree.winfo_reqheight() or 260
                print(f"Detail width: {detail_width}, Description width: {desc_width}, Tree height: {tree_height}, Details height: {self.detail_frame.winfo_height()}")
            else:
                print("Transaction tree destroyed during population")

        self.root.after(100, set_columns)  # Increased delay to 100ms

    def show_transaction_history_from_toolbar(self):
        path = self.get_selected_path()
        if not path:
            return
        try:
            category = self.get_category(path)
            if not category.get("transactions", []):
                messagebox.showwarning("Warning", "No transactions to display for this category.")
                return
            self.show_transaction_history_popup(category, self.detail_content.winfo_width() or 600)
        except KeyError:
            messagebox.showerror("Error", f"Cannot load transactions for '{path}'.")

    def show_transaction_history_popup(self, category, table_width):
        # Create pop-up window
        popup = tk.Toplevel(self.root)
        popup.title("Transaction History")
        tree_height = 260  # Approx 25px/row * 10 + header (~30px)
        popup_width = max(550, table_width)
        popup_height = tree_height + 20
        popup.geometry(f"{popup_width}x{popup_height}")
        popup.minsize(popup_width, popup_height)
        popup.resizable(True, True)
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        # Update pop-up geometry
        popup.update_idletasks()

        # Create main frame
        main_frame = ttk.Frame(popup, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Transaction Treeview with scrollbar
        tree = ttk.Treeview(main_frame, columns=("Date", "Amount", "Description"), selectmode="none")
        tree.heading("Date", text="Date")
        tree.heading("Amount", text="Amount (€)")
        tree.heading("Description", text="Description")

        # Hide the #0 column
        tree.column("#0", width=0, stretch=False, minwidth=0)

        # Calculate available width
        scrollbar_width = 12
        padding = 15
        available_width = popup_width - padding - scrollbar_width
        desc_width = max(200, available_width - 150 - 100)
        tree_width = 150 + 100 + desc_width

        tree.column("Date", width=150, minwidth=150, stretch=False, anchor="center")
        tree.column("Amount", width=100, minwidth=100, stretch=False, anchor="center")
        tree.column("Description", width=int(desc_width), minwidth=200, stretch=False, anchor="w")

        # Prevent column resizing
        def block_resize(event):
            return "break"
        tree.bind("<Button-1>", block_resize, add="+")

        # Add scrollbar directly to Treeview
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview, style="Narrow.Vertical.TScrollbar")
        tree.configure(yscrollcommand=v_scrollbar.set)

        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Populate all transactions
        transactions = sorted(category["transactions"], key=lambda x: x.get("timestamp", ""), reverse=True)
        for trans in transactions:
            tree.insert("", "end", values=(
                trans.get("timestamp", "N/A"),
                f"{trans.get('amount', 0.0):.2f}",
                trans.get("description", "(No description)")
            ))

        # Mouse wheel scrolling
        def on_mouse_wheel(event):
            tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        tree.bind("<MouseWheel>", on_mouse_wheel)
        tree.bind("<Button-4>", lambda e: tree.yview_scroll(-1, "units"))
        tree.bind("<Button-5>", lambda e: tree.yview_scroll(1, "units"))

        # Adjust Treeview height to show up to 10 rows, scrollbar handles overflow
        tree["height"] = min(10, len(transactions))
        tree.update_idletasks()
        print(f"Popup actual width: {popup.winfo_width()}, Popup width: {popup_width}, Scrollbar width: {scrollbar_width}, Description width: {desc_width}, Tree width: {tree_width}, Tree height: {tree['height']}, Transactions: {len(transactions)}, Tree visible: {tree.winfo_ismapped()}")

    def show_summary_details(self, category):
        # Create main frame
        main_frame = ttk.Frame(self.detail_content, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=0)  # Label row
        main_frame.grid_rowconfigure(1, weight=1)  # Child list row
        main_frame.grid_columnconfigure(0, weight=1)

        # Add "Wallets:" label
        ttk.Label(main_frame, text="Wallets:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, pady=(0, 5), sticky=tk.W)

        # Create frame for child list
        child_frame = ttk.Frame(main_frame)
        child_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        child_frame.grid_columnconfigure(0, weight=1)

        # Populate child list or show "None"
        children = category["children"]
        if not children:
            ttk.Label(child_frame, text="None").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        else:
            for i, (name, data) in enumerate(sorted(children.items())):
                child_text = f"{name} ({data['type']})"
                print(f"Adding child: {child_text}")
                ttk.Label(child_frame, text=child_text).grid(row=i, column=0, padx=10, pady=2, sticky=tk.W)

        main_frame.update_idletasks()
        print(f"Summary details height: {main_frame.winfo_height()}, Details height: {self.detail_frame.winfo_height()}")

    def update_history_button_state(self):
        path = self.get_selected_path(silent=True) if self.tree.get_children() else None
        if path:
            try:
                category = self.get_category(path)
                self.history_button.config(state="normal" if category.get("transactions", []) else "disabled")
            except KeyError:
                self.history_button.config(state="disabled")
        else:
            self.history_button.config(state="disabled")

    def get_selected_path(self, silent=False):
        selected = self.tree.selection()
        if not selected:
            if not silent:
                messagebox.showwarning("Warning", "Please select a category first.")
            return None
        item = self.tree.item(selected[0])
        path_parts = []
        current_iid = selected[0]
        while current_iid:
            item_text = self.tree.item(current_iid)["text"].split(" (")[0]
            path_parts.insert(0, item_text)
            current_iid = self.tree.parent(current_iid)
        full_path = ".".join(path_parts)
        try:
            self.get_category(full_path)
            return full_path
        except KeyError as e:
            if not silent:
                messagebox.showerror("Error", f"Invalid category path: {full_path}. {str(e)}")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceManager(root)
    root.mainloop()