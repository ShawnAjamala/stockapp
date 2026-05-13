"""
WAREHOUSE STOCK MANAGEMENT - Complete Working Version
Add, Edit, Delete products with scrollable product list
"""
import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    create_warehouse_product, 
    get_all_warehouse_products, 
    update_warehouse_product, 
    delete_warehouse_product,
    search_warehouse_products
)

class WarehouseStock(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.configure(bg='#F5F6FA')
        self.current_selected_product = None
        
        self.create_widgets()
        self.load_stock()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="WAREHOUSE STOCK MANAGEMENT", 
                font=("Segoe UI", 20, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Main container with two columns
        main_container = tk.Frame(self, bg='#F5F6FA')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # LEFT SIDE - FORM
        form_frame = tk.LabelFrame(main_container, text="PRODUCT FORM", 
                                   font=("Segoe UI", 12, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        form_frame.pack(side='left', fill='y', padx=(0, 10), pady=5)
        
        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(pady=20, padx=20)
        
        # Product Name
        tk.Label(form_inner, text="Product Name:", font=("Segoe UI", 11), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.entry_name = tk.Entry(form_inner, width=25, font=("Segoe UI", 11), 
                                    relief='solid', bd=1)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)
        
        # Quantity
        tk.Label(form_inner, text="Quantity (KG):", font=("Segoe UI", 11), 
                bg='#FFFFFF').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.entry_qty = tk.Entry(form_inner, width=25, font=("Segoe UI", 11), 
                                   relief='solid', bd=1)
        self.entry_qty.grid(row=1, column=1, padx=10, pady=10)
        
        # Price
        tk.Label(form_inner, text="Price per KG ($):", font=("Segoe UI", 11), 
                bg='#FFFFFF').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.entry_price = tk.Entry(form_inner, width=25, font=("Segoe UI", 11), 
                                     relief='solid', bd=1)
        self.entry_price.grid(row=2, column=1, padx=10, pady=10)
        
        # Buttons Frame
        button_frame = tk.Frame(form_inner, bg='#FFFFFF')
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Add Button
        self.btn_add = tk.Button(button_frame, text="ADD PRODUCT", command=self.add_product,
                                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"),
                                 relief='flat', cursor='hand2', padx=15, pady=5)
        self.btn_add.pack(side='left', padx=5)
        
        # Update Button
        self.btn_update = tk.Button(button_frame, text="UPDATE PRODUCT", command=self.update_product,
                                    bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold"),
                                    relief='flat', cursor='hand2', padx=15, pady=5)
        self.btn_update.pack(side='left', padx=5)
        
        # Delete Button
        self.btn_delete = tk.Button(button_frame, text="DELETE PRODUCT", command=self.delete_product,
                                    bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"),
                                    relief='flat', cursor='hand2', padx=15, pady=5)
        self.btn_delete.pack(side='left', padx=5)
        
        # Clear Button
        self.btn_clear = tk.Button(button_frame, text="CLEAR FORM", command=self.clear_form,
                                   bg='#95A5A6', fg='white', font=("Segoe UI", 10, "bold"),
                                   relief='flat', cursor='hand2', padx=15, pady=5)
        self.btn_clear.pack(side='left', padx=5)
        
        # Disable update and delete initially
        self.btn_update.config(state='disabled', bg='#95A5A6')
        self.btn_delete.config(state='disabled', bg='#95A5A6')
        
        # RIGHT SIDE - PRODUCT LIST (SCROLLABLE)
        list_frame = tk.LabelFrame(main_container, text="PRODUCT LIST", 
                                   font=("Segoe UI", 12, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        list_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=5)
        
        # Search bar
        search_inner = tk.Frame(list_frame, bg='#FFFFFF')
        search_inner.pack(fill="x", pady=10, padx=10)
        
        tk.Label(search_inner, text="Search:", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_inner, width=30, font=("Segoe UI", 10), 
                                      relief='solid', bd=1)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(search_inner, text="SEARCH", command=self.search_products,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        tk.Button(search_inner, text="REFRESH", command=self.load_stock,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        # Scrollable Table Frame
        table_container = tk.Frame(list_frame, bg='#FFFFFF')
        table_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(table_container, bg='#FFFFFF', highlightthickness=0)
        scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Treeview inside scrollable frame
        columns = ('Name', 'Quantity', 'Price', 'Total')
        self.tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings', height=12)
        
        self.tree.heading('Name', text='Product Name')
        self.tree.heading('Quantity', text='Quantity (KG)')
        self.tree.heading('Price', text='Price per KG ($)')
        self.tree.heading('Total', text='Total Value ($)')
        
        self.tree.column('Name', width=200)
        self.tree.column('Quantity', width=120)
        self.tree.column('Price', width=120)
        self.tree.column('Total', width=150)
        
        # Bind select event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        self.tree.pack(fill='both', expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Total value display
        total_frame = tk.Frame(list_frame, bg='#FEF9E7', relief='solid', bd=1)
        total_frame.pack(fill="x", pady=10, padx=10)
        
        tk.Label(total_frame, text="TOTAL INVENTORY VALUE:", font=("Segoe UI", 11, "bold"), 
                bg='#FEF9E7', fg='#E67E22').pack(side='left', padx=15, pady=8)
        
        self.total_value_label = tk.Label(total_frame, text="$0.00", font=("Segoe UI", 14, "bold"), 
                                          bg='#FEF9E7', fg='#27AE60')
        self.total_value_label.pack(side='right', padx=15, pady=8)
    
    def load_stock(self):
        """Load all products into the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = get_all_warehouse_products()
        
        for p in products:
            total = p['quantity'] * p['price']
            self.tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:.2f} KG",
                f"${p['price']:.2f}",
                f"${total:.2f}"
            ))
        
        total_value = sum(p['quantity'] * p['price'] for p in products)
        self.total_value_label.config(text=f"${total_value:,.2f}")
    
    def search_products(self):
        """Search products by name"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_stock()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = search_warehouse_products(keyword)
        
        for p in products:
            total = p['quantity'] * p['price']
            self.tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:.2f} KG",
                f"${p['price']:.2f}",
                f"${total:.2f}"
            ))
        
        search_value = sum(p['quantity'] * p['price'] for p in products)
        self.total_value_label.config(text=f"${search_value:,.2f}")
    
    def on_select(self, event):
        """When a product is selected, load it into the form"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if values:
            product_name = values[0]
            quantity_str = values[1].replace(' KG', '')
            price_str = values[2].replace('$', '')
            
            self.current_selected_product = product_name
            
            # Load into form
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, product_name)
            self.entry_name.config(state='readonly')
            
            self.entry_qty.delete(0, tk.END)
            self.entry_qty.insert(0, quantity_str)
            
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, price_str)
            
            # Enable update and delete buttons
            self.btn_update.config(state='normal', bg='#F39C12')
            self.btn_delete.config(state='normal', bg='#E74C3C')
            self.btn_add.config(state='disabled', bg='#95A5A6')
    
    def clear_form(self):
        """Clear the form and reset to add mode"""
        self.entry_name.config(state='normal')
        self.entry_name.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.current_selected_product = None
        
        # Reset buttons
        self.btn_add.config(state='normal', bg='#27AE60')
        self.btn_update.config(state='disabled', bg='#95A5A6')
        self.btn_delete.config(state='disabled', bg='#95A5A6')
    
    def add_product(self):
        """Add new product to warehouse"""
        name = self.entry_name.get().strip()
        qty = self.entry_qty.get().strip()
        price = self.entry_price.get().strip()
        
        if not name or not qty or not price:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            qty = float(qty)
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
    
    def update_product(self):
        """Update the selected product"""
        if not self.current_selected_product:
            messagebox.showerror("Error", "No product selected")
            return
        
        name = self.entry_name.get().strip()
        qty = self.entry_qty.get().strip()
        price = self.entry_price.get().strip()
        
        try:
            qty = float(qty)
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
    
    def delete_product(self):
        """Delete the selected product"""
        if not self.current_selected_product:
            messagebox.showerror("Error", "No product selected")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete '{self.current_selected_product}'?\n\nThis action cannot be undone!")
        
        if result:
            success, message = delete_warehouse_product(self.current_selected_product)
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_stock()
            else:
                messagebox.showerror("Error", message)