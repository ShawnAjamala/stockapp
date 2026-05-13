import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    get_all_warehouse_products,
    get_all_supermarket_products,
    receive_stock_from_warehouse,
    update_selling_price,
    get_unread_alerts
)

class SupermarketReceive(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user
        self.refresh_callback = refresh_callback
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
        self.load_warehouse_products()
        self.load_supermarket_products()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="RECEIVE STOCK & SET SELLING PRICE", 
                font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Create two columns
        left_frame = tk.Frame(self, bg='#F5F6FA')
        left_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        right_frame = tk.Frame(self, bg='#F5F6FA')
        right_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        # LEFT SECTION: Receive Stock from Warehouse
        receive_frame = tk.LabelFrame(left_frame, text="RECEIVE STOCK FROM WAREHOUSE", 
                                      font=("Segoe UI", 12, "bold"), 
                                      bg='#FFFFFF', fg='#E67E22')
        receive_frame.pack(fill="both", expand=True, pady=10)
        
        receive_inner = tk.Frame(receive_frame, bg='#FFFFFF')
        receive_inner.pack(pady=20, padx=20)
        
        # Select product from warehouse
        tk.Label(receive_inner, text="Select Product:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_select = ttk.Combobox(receive_inner, width=30, font=("Segoe UI", 10), state='readonly')
        self.product_select.grid(row=0, column=1, padx=10, pady=10)
        self.product_select.bind('<<ComboboxSelected>>', self.on_product_select)
        
        # Available stock in warehouse
        tk.Label(receive_inner, text="Available in Warehouse:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.available_label = tk.Label(receive_inner, text="0 KG", font=("Segoe UI", 10, "bold"), 
                                        bg='#FFFFFF', fg='#27AE60')
        self.available_label.grid(row=0, column=3, padx=10, pady=10)
        
        # Cost price (from warehouse)
        tk.Label(receive_inner, text="Cost Price (per KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.cost_label = tk.Label(receive_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        self.cost_label.grid(row=1, column=1, padx=10, pady=10)
        
        # Quantity to receive
        tk.Label(receive_inner, text="Quantity to Receive (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.receive_qty = tk.Entry(receive_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.receive_qty.grid(row=1, column=3, padx=10, pady=10)
        
        # Receiving warehouse email
        tk.Label(receive_inner, text="From Warehouse (Email):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.warehouse_email = tk.Entry(receive_inner, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        self.warehouse_email.grid(row=2, column=1, padx=10, pady=10, columnspan=3)
        
        # Receive button
        tk.Button(receive_inner, text="RECEIVE STOCK", command=self.receive_stock,
                 bg='#27AE60', fg='white', font=("Segoe UI", 11, "bold"), 
                 relief='flat', cursor='hand2', padx=30, pady=8).grid(row=3, column=0, columnspan=4, pady=20)
        
        # RIGHT SECTION: Set Selling Price for Received Products
        price_frame = tk.LabelFrame(right_frame, text="SET SELLING PRICE", 
                                    font=("Segoe UI", 12, "bold"), 
                                    bg='#FFFFFF', fg='#E67E22')
        price_frame.pack(fill="both", expand=True, pady=10)
        
        price_inner = tk.Frame(price_frame, bg='#FFFFFF')
        price_inner.pack(pady=20, padx=20)
        
        # Select supermarket product
        tk.Label(price_inner, text="Select Product:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.supermarket_product_select = ttk.Combobox(price_inner, width=30, font=("Segoe UI", 10), state='readonly')
        self.supermarket_product_select.grid(row=0, column=1, padx=10, pady=10)
        self.supermarket_product_select.bind('<<ComboboxSelected>>', self.on_supermarket_product_select)
        
        # Current stock
        tk.Label(price_inner, text="Current Stock:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.current_stock_label = tk.Label(price_inner, text="0 KG", font=("Segoe UI", 10, "bold"), 
                                            bg='#FFFFFF', fg='#27AE60')
        self.current_stock_label.grid(row=0, column=3, padx=10, pady=10)
        
        # Cost price display
        tk.Label(price_inner, text="Cost Price (per KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.cost_display_label = tk.Label(price_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                           bg='#FFFFFF', fg='#E67E22')
        self.cost_display_label.grid(row=1, column=1, padx=10, pady=10)
        
        # Selling price input
        tk.Label(price_inner, text="Selling Price (per KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.selling_price_entry = tk.Entry(price_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.selling_price_entry.grid(row=1, column=3, padx=10, pady=10)
        
        # Potential profit preview
        tk.Label(price_inner, text="Profit per KG:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.profit_preview = tk.Label(price_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                       bg='#FFFFFF', fg='#27AE60')
        self.profit_preview.grid(row=2, column=1, padx=10, pady=10)
        
        # Update price button
        tk.Button(price_inner, text="UPDATE SELLING PRICE", command=self.update_selling_price,
                 bg='#3498DB', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=8).grid(row=2, column=2, columnspan=2, pady=10)
        
        self.selling_price_entry.bind('<KeyRelease>', self.update_profit_preview)
    
    def load_warehouse_products(self):
        # Load warehouse products into dropdown
        products = get_all_warehouse_products()
        self.warehouse_product_list = {p['name']: p for p in products}
        self.product_select['values'] = list(self.warehouse_product_list.keys())
    
    def load_supermarket_products(self):
        # Load supermarket products into dropdown for selling price setup
        products = get_all_supermarket_products()
        self.supermarket_product_list = {p['name']: p for p in products}
        self.supermarket_product_select['values'] = list(self.supermarket_product_list.keys())
    
    def on_product_select(self, event):
        # When product is selected, show available stock and cost price
        product_name = self.product_select.get()
        if product_name in self.warehouse_product_list:
            product = self.warehouse_product_list[product_name]
            self.available_label.config(text=f"{product['quantity']:,.2f} KG")
            self.cost_label.config(text=f"${product['price']:,.2f}")
    
    def on_supermarket_product_select(self, event):
        # When supermarket product is selected, show current stock and cost price
        product_name = self.supermarket_product_select.get()
        if product_name in self.supermarket_product_list:
            product = self.supermarket_product_list[product_name]
            self.current_stock_label.config(text=f"{product['quantity']:,.2f} KG")
            self.cost_display_label.config(text=f"${product.get('cost_price', 0):,.2f}")
            current_selling = product.get('selling_price', 0)
            if current_selling > 0:
                self.selling_price_entry.delete(0, tk.END)
                self.selling_price_entry.insert(0, f"{current_selling:.2f}")
            self.update_profit_preview()
    
    def update_profit_preview(self, event=None):
        # Calculate and display profit per KG based on selling price
        try:
            product_name = self.supermarket_product_select.get()
            if product_name in self.supermarket_product_list:
                cost = self.supermarket_product_list[product_name].get('cost_price', 0)
                selling = float(self.selling_price_entry.get().strip()) if self.selling_price_entry.get().strip() else 0
                profit = selling - cost
                self.profit_preview.config(text=f"${profit:,.2f}", fg='#27AE60' if profit > 0 else '#E74C3C')
            else:
                self.profit_preview.config(text="$0.00")
        except:
            self.profit_preview.config(text="$0.00")
    
    def receive_stock(self):
        # Receive stock from warehouse
        product_name = self.product_select.get()
        quantity_str = self.receive_qty.get().strip()
        warehouse_email = self.warehouse_email.get().strip()
        
        if not product_name:
            messagebox.showerror("Error", "Please select a product")
            return
        
        if not quantity_str:
            messagebox.showerror("Error", "Please enter quantity to receive")
            return
        
        if not warehouse_email:
            messagebox.showerror("Error", "Please enter warehouse email")
            return
        
        try:
            quantity = float(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid number")
            return
        
        if product_name not in self.warehouse_product_list:
            messagebox.showerror("Error", "Product not found in warehouse")
            return
        
        warehouse_product = self.warehouse_product_list[product_name]
        
        if warehouse_product['quantity'] < quantity:
            messagebox.showerror("Error", f"Insufficient stock. Only {warehouse_product['quantity']:.2f} KG available")
            return
        
        # Update warehouse stock (deduct)
        new_warehouse_qty = warehouse_product['quantity'] - quantity
        from db import update_warehouse_product
        update_warehouse_product(product_name, new_warehouse_qty, warehouse_product['price'])
        
        # Receive stock to supermarket
        success, message = receive_stock_from_warehouse(
            product_name, quantity, warehouse_product['price'], warehouse_email
        )
        
        if success:
            messagebox.showinfo("Success", message)
            # Refresh the supermarket products list
            self.load_supermarket_products()
            # Clear form
            self.receive_qty.delete(0, tk.END)
            self.warehouse_email.delete(0, tk.END)
            self.product_select.set('')
            self.available_label.config(text="0 KG")
            # Refresh dashboard if callback exists
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", message)
    
    def update_selling_price(self):
        # Update selling price for supermarket product
        product_name = self.supermarket_product_select.get()
        selling_price_str = self.selling_price_entry.get().strip()
        
        if not product_name:
            messagebox.showerror("Error", "Please select a product")
            return
        
        if not selling_price_str:
            messagebox.showerror("Error", "Please enter selling price")
            return
        
        try:
            selling_price = float(selling_price_str)
        except ValueError:
            messagebox.showerror("Error", "Selling price must be a valid number")
            return
        
        success, message = update_selling_price(product_name, selling_price)
        
        if success:
            messagebox.showinfo("Success", message)
            # Refresh the product list
            self.load_supermarket_products()
        else:
            messagebox.showerror("Error", message)