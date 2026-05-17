# WAREHOUSE STOCK MANAGEMENT - Responsive layout, fills correctly when enlarged
import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    create_warehouse_product,
    get_all_warehouse_products,
    update_warehouse_product,
    delete_warehouse_product,
    search_warehouse_products
)

# Main class for warehouse stock management (add, edit, delete, search)
class WarehouseStock(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user                         # currently logged‑in warehouse admin
        self.refresh_callback = refresh_callback # function to refresh dashboard stats
        self.configure(bg='#F5F6FA')
        self.current_selected_product = None     # stores name of selected product for edit/delete

        self.create_widgets()
        self.load_stock()

    # Safe callback helper – only fires if this frame is still alive
    def _try_refresh(self):
        try:
            if self.winfo_exists() and self.refresh_callback:
                self.refresh_callback()
        except Exception:
            pass

    # Build the entire user interface
    def create_widgets(self):
        # ---- Header section ----
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="WAREHOUSE STOCK MANAGEMENT",
                 font=("Segoe UI", 20, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=16)

        # ---- Main container – grid layout, left column (form), right column (list) ----
        main_container = tk.Frame(self, bg='#F5F6FA')
        main_container.pack(fill="both", expand=True, padx=12, pady=8)

        # Column 0 = form (fixed width), column 1 = product list (expands)
        main_container.columnconfigure(0, weight=0)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # ---- LEFT COLUMN: Product form (add/edit) ----
        form_frame = tk.LabelFrame(main_container, text="PRODUCT FORM",
                                   font=("Segoe UI", 12, "bold"),
                                   bg='#FFFFFF', fg='#E67E22')
        form_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=4)

        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(fill='both', expand=True, pady=20, padx=20)
        form_inner.columnconfigure(1, weight=1)   # make entry fields expand horizontally

        # Common styling for labels and entries
        lbl_cfg = dict(font=("Segoe UI", 11), bg='#FFFFFF', anchor='w')
        ent_cfg = dict(font=("Segoe UI", 11), relief='solid', bd=1)

        # Product name entry
        tk.Label(form_inner, text="Product Name:", **lbl_cfg).grid(
            row=0, column=0, padx=(0, 10), pady=10, sticky='w')
        self.entry_name = tk.Entry(form_inner, width=28, **ent_cfg)
        self.entry_name.grid(row=0, column=1, pady=10, sticky='ew')

        # Quantity (KG) entry
        tk.Label(form_inner, text="Quantity (KG):", **lbl_cfg).grid(
            row=1, column=0, padx=(0, 10), pady=10, sticky='w')
        self.entry_qty = tk.Entry(form_inner, width=28, **ent_cfg)
        self.entry_qty.grid(row=1, column=1, pady=10, sticky='ew')

        # Price per KG entry
        tk.Label(form_inner, text="Price per KG ($):", **lbl_cfg).grid(
            row=2, column=0, padx=(0, 10), pady=10, sticky='w')
        self.entry_price = tk.Entry(form_inner, width=28, **ent_cfg)
        self.entry_price.grid(row=2, column=1, pady=10, sticky='ew')

        # ---- Action buttons (stacked vertically) ----
        btn_frame = tk.Frame(form_inner, bg='#FFFFFF')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky='ew')

        # Common button styling
        btn_cfg = dict(font=("Segoe UI", 10, "bold"), relief='flat',
                       cursor='hand2', fg='white', pady=7)

        # Add button (green)
        self.btn_add = tk.Button(btn_frame, text="ADD PRODUCT",
                                 command=self.add_product, bg='#27AE60', **btn_cfg)
        self.btn_add.pack(fill='x', pady=3)

        # Update button (orange) – initially disabled
        self.btn_update = tk.Button(btn_frame, text="UPDATE PRODUCT",
                                    command=self.update_product, bg='#F39C12', **btn_cfg)
        self.btn_update.pack(fill='x', pady=3)
        self.btn_update.config(state='disabled', bg='#BDC3C7')

        # Delete button (red) – initially disabled
        self.btn_delete = tk.Button(btn_frame, text="DELETE PRODUCT",
                                    command=self.delete_product, bg='#E74C3C', **btn_cfg)
        self.btn_delete.pack(fill='x', pady=3)
        self.btn_delete.config(state='disabled', bg='#BDC3C7')

        # Clear button (grey)
        self.btn_clear = tk.Button(btn_frame, text="CLEAR FORM",
                                   command=self.clear_form, bg='#95A5A6', **btn_cfg)
        self.btn_clear.pack(fill='x', pady=3)

        # ---- RIGHT COLUMN: Product list with search and scrollbars ----
        list_frame = tk.LabelFrame(main_container, text="PRODUCT LIST",
                                   font=("Segoe UI", 12, "bold"),
                                   bg='#FFFFFF', fg='#E67E22')
        list_frame.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=4)

        # Make the list_frame's interior expand properly
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)   # row 1 holds the Treeview

        # Search bar row
        search_bar = tk.Frame(list_frame, bg='#FFFFFF')
        search_bar.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        tk.Label(search_bar, text="Search:", font=("Segoe UI", 10),
                 bg='#FFFFFF').pack(side='left', padx=(0, 5))
        self.search_entry = tk.Entry(search_bar, font=("Segoe UI", 10),
                                     relief='solid', bd=1)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 6))

        tk.Button(search_bar, text="SEARCH", command=self.search_products,
                  bg='#3498DB', fg='white', font=("Segoe UI", 9),
                  relief='flat', padx=14, pady=4).pack(side='left', padx=3)
        tk.Button(search_bar, text="REFRESH", command=self.load_stock,
                  bg='#95A5A6', fg='white', font=("Segoe UI", 9),
                  relief='flat', padx=14, pady=4).pack(side='left', padx=3)

        # Treeview container with vertical and horizontal scrollbars
        tree_container = tk.Frame(list_frame, bg='#FFFFFF')
        tree_container.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(tree_container, orient='vertical')
        v_scroll.grid(row=0, column=1, sticky='ns')

        h_scroll = ttk.Scrollbar(tree_container, orient='horizontal')
        h_scroll.grid(row=1, column=0, sticky='ew')

        # Treeview columns
        columns = ('Name', 'Quantity', 'Price', 'Total')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set,
                                 xscrollcommand=h_scroll.set)
        self.tree.grid(row=0, column=0, sticky='nsew')

        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        # Column headings and alignment
        self.tree.heading('Name',     text='Product Name',    anchor='w')
        self.tree.heading('Quantity', text='Quantity (KG)',    anchor='center')
        self.tree.heading('Price',    text='Price per KG ($)', anchor='center')
        self.tree.heading('Total',    text='Total Value ($)',  anchor='center')

        # Column widths and stretch behaviour
        self.tree.column('Name',     minwidth=160, width=220, stretch=True,  anchor='w')
        self.tree.column('Quantity', minwidth=100, width=130, stretch=True,  anchor='center')
        self.tree.column('Price',    minwidth=110, width=140, stretch=True,  anchor='center')
        self.tree.column('Total',    minwidth=120, width=150, stretch=True,  anchor='center')

        # Alternating row colours for better readability
        self.tree.tag_configure('odd',  background='#FDFEFE')
        self.tree.tag_configure('even', background='#EBF5FB')

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # ---- Total inventory value bar (below the table) ----
        total_frame = tk.Frame(list_frame, bg='#FEF9E7', relief='solid', bd=1)
        total_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))

        tk.Label(total_frame, text="TOTAL INVENTORY VALUE:",
                 font=("Segoe UI", 11, "bold"), bg='#FEF9E7', fg='#E67E22'
                 ).pack(side='left', padx=15, pady=8)

        self.total_value_label = tk.Label(total_frame, text="$0.00",
                                          font=("Segoe UI", 14, "bold"),
                                          bg='#FEF9E7', fg='#27AE60')
        self.total_value_label.pack(side='right', padx=15, pady=8)

    # Load all warehouse products from database into the treeview
    def load_stock(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = get_all_warehouse_products()
        total_value = 0
        for idx, p in enumerate(products):
            total = p['quantity'] * p['price']
            total_value += total
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert('', 'end', tags=(tag,), values=(
                p['name'],
                f"{p['quantity']:.2f} KG",
                f"${p['price']:.2f}",
                f"${total:.2f}"
            ))

        self.total_value_label.config(text=f"${total_value:,.2f}")
        self._try_refresh()

    # Search products by name and refresh the treeview
    def search_products(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_stock()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        products = search_warehouse_products(keyword)
        total_value = 0
        for idx, p in enumerate(products):
            total = p['quantity'] * p['price']
            total_value += total
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert('', 'end', tags=(tag,), values=(
                p['name'],
                f"{p['quantity']:.2f} KG",
                f"${p['price']:.2f}",
                f"${total:.2f}"
            ))

        self.total_value_label.config(text=f"${total_value:,.2f}")

    # When a product row is selected, populate the form for editing
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        if not values:
            return

        product_name = values[0]
        quantity_str = str(values[1]).replace(' KG', '')
        price_str    = str(values[2]).replace('$', '')

        self.current_selected_product = product_name

        # Temporarily enable name entry to clear, then set to readonly
        self.entry_name.config(state='normal')
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, product_name)
        self.entry_name.config(state='readonly')

        self.entry_qty.delete(0, tk.END)
        self.entry_qty.insert(0, quantity_str)

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, price_str)

        # Enable update and delete buttons, disable add
        self.btn_update.config(state='normal',   bg='#F39C12')
        self.btn_delete.config(state='normal',   bg='#E74C3C')
        self.btn_add.config(state='disabled',    bg='#BDC3C7')

    # Clear the form and reset to "add" mode
    def clear_form(self):
        self.entry_name.config(state='normal')
        self.entry_name.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.current_selected_product = None

        # Reset buttons: add enabled, update/delete disabled
        self.btn_add.config(state='normal',      bg='#27AE60')
        self.btn_update.config(state='disabled', bg='#BDC3C7')
        self.btn_delete.config(state='disabled', bg='#BDC3C7')

    # Add a new product to the warehouse
    def add_product(self):
        name  = self.entry_name.get().strip()
        qty   = self.entry_qty.get().strip()
        price = self.entry_price.get().strip()

        if not name or not qty or not price:
            messagebox.showerror("Error", "Please fill all fields")
            return
        try:
            qty   = float(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        if price <= 0:
            messagebox.showerror("Error", "Price must be greater than 0")
            return

        success, message = create_warehouse_product(name, qty, price)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_stock()
        else:
            messagebox.showerror("Error", message)

    # Update the currently selected product
    def update_product(self):
        if not self.current_selected_product:
            messagebox.showerror("Error", "No product selected")
            return

        name  = self.entry_name.get().strip()
        qty   = self.entry_qty.get().strip()
        price = self.entry_price.get().strip()

        try:
            qty   = float(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        if price <= 0:
            messagebox.showerror("Error", "Price must be greater than 0")
            return

        success, message = update_warehouse_product(name, qty, price)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_stock()
        else:
            messagebox.showerror("Error", message)

    # Delete the currently selected product (with confirmation)
    def delete_product(self):
        if not self.current_selected_product:
            messagebox.showerror("Error", "No product selected")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.current_selected_product}'?\n\nThis action cannot be undone!"
        ):
            success, message = delete_warehouse_product(self.current_selected_product)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_stock()
            else:
                messagebox.showerror("Error", message)