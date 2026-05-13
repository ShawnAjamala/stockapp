import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    get_all_supermarket_products,
    record_sale,
    get_today_sales,
    get_all_sales
)

class SupermarketSales(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user
        self.refresh_callback = refresh_callback
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
        self.load_products()
        self.load_today_sales()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="RECORD SALES", 
                font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Create two columns - left for sales form, right for today's sales
        left_frame = tk.Frame(self, bg='#F5F6FA')
        left_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        right_frame = tk.Frame(self, bg='#F5F6FA')
        right_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        # ========== LEFT SECTION - Record Sale Form ==========
        form_frame = tk.LabelFrame(left_frame, text="RECORD NEW SALE", 
                                   font=("Segoe UI", 12, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        form_frame.pack(fill="x", pady=10)
        
        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(pady=20, padx=20)
        
        # Select Product
        tk.Label(form_inner, text="Select Product:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_select = ttk.Combobox(form_inner, width=30, font=("Segoe UI", 10), state='readonly')
        self.product_select.grid(row=0, column=1, padx=10, pady=10)
        self.product_select.bind('<<ComboboxSelected>>', self.on_product_select)
        
        # Available Stock
        tk.Label(form_inner, text="Available Stock:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.available_label = tk.Label(form_inner, text="0 KG", font=("Segoe UI", 10, "bold"), 
                                        bg='#FFFFFF', fg='#27AE60')
        self.available_label.grid(row=0, column=3, padx=10, pady=10)
        
        # Cost Price (for reference)
        tk.Label(form_inner, text="Cost Price (per KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.cost_label = tk.Label(form_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        self.cost_label.grid(row=1, column=1, padx=10, pady=10)
        
        # Selling Price (per KG)
        tk.Label(form_inner, text="Selling Price (per KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.selling_price_entry = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.selling_price_entry.grid(row=1, column=3, padx=10, pady=10)
        self.selling_price_entry.bind('<KeyRelease>', self.update_profit_preview)
        
        # Quantity Sold
        tk.Label(form_inner, text="Quantity Sold (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.quantity_entry = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=10)
        self.quantity_entry.bind('<KeyRelease>', self.update_profit_preview)
        
        # Profit Preview
        tk.Label(form_inner, text="Profit on this sale:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=2, column=2, padx=10, pady=10, sticky='w')
        self.profit_preview = tk.Label(form_inner, text="$0.00", font=("Segoe UI", 11, "bold"), 
                                       bg='#FFFFFF', fg='#27AE60')
        self.profit_preview.grid(row=2, column=3, padx=10, pady=10)
        
        # Record Sale Button
        tk.Button(form_inner, text="RECORD SALE", command=self.record_sale,
                 bg='#27AE60', fg='white', font=("Segoe UI", 11, "bold"), 
                 relief='flat', cursor='hand2', padx=30, pady=10).grid(row=3, column=0, columnspan=4, pady=20)
        
        # ========== RIGHT SECTION - Today's Sales ==========
        sales_frame = tk.LabelFrame(right_frame, text="TODAY'S SALES", 
                                    font=("Segoe UI", 12, "bold"), 
                                    bg='#FFFFFF', fg='#E67E22')
        sales_frame.pack(fill="both", expand=True, pady=10)
        
        # Summary bar
        summary_frame = tk.Frame(sales_frame, bg='#FEF9E7', relief='solid', bd=1)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_sales_label = tk.Label(summary_frame, text="Today's Total Sales: 0 KG", 
                                          font=("Segoe UI", 11, "bold"), 
                                          bg='#FEF9E7', fg='#E67E22')
        self.total_sales_label.pack(side='left', padx=15, pady=8)
        
        self.total_profit_label = tk.Label(summary_frame, text="Today's Total Profit: $0.00", 
                                           font=("Segoe UI", 11, "bold"), 
                                           bg='#FEF9E7', fg='#27AE60')
        self.total_profit_label.pack(side='right', padx=15, pady=8)
        
        # Sales table
        table_frame = tk.Frame(sales_frame, bg='#FFFFFF')
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ('Product', 'Quantity', 'Selling Price', 'Cost Price', 'Profit', 'Time')
        self.sales_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        self.sales_tree.heading('Product', text='Product Name')
        self.sales_tree.heading('Quantity', text='Quantity (KG)')
        self.sales_tree.heading('Selling Price', text='Selling Price ($/KG)')
        self.sales_tree.heading('Cost Price', text='Cost Price ($/KG)')
        self.sales_tree.heading('Profit', text='Profit ($)')
        self.sales_tree.heading('Time', text='Time')
        
        self.sales_tree.column('Product', width=150)
        self.sales_tree.column('Quantity', width=100)
        self.sales_tree.column('Selling Price', width=120)
        self.sales_tree.column('Cost Price', width=120)
        self.sales_tree.column('Profit', width=100)
        self.sales_tree.column('Time', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Refresh button
        tk.Button(sales_frame, text="REFRESH SALES", command=self.load_today_sales,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9, "bold"), 
                 relief='flat', cursor='hand2', padx=15, pady=5).pack(pady=10)
    
    def load_products(self):
        # Load supermarket products that have selling price set and stock > 0
        products = get_all_supermarket_products()
        # Only show products with stock > 0
        self.product_list = {}
        for p in products:
            if p['quantity'] > 0:
                self.product_list[p['name']] = p
        self.product_select['values'] = list(self.product_list.keys())
    
    def on_product_select(self, event):
        # When product is selected, show its details
        product_name = self.product_select.get()
        if product_name in self.product_list:
            product = self.product_list[product_name]
            self.available_label.config(text=f"{product['quantity']:.2f} KG")
            self.cost_label.config(text=f"${product.get('cost_price', 0):.2f}")
            
            # Pre-fill selling price if already set
            selling_price = product.get('selling_price', 0)
            if selling_price > 0:
                self.selling_price_entry.delete(0, tk.END)
                self.selling_price_entry.insert(0, f"{selling_price:.2f}")
            
            # Clear quantity and profit preview
            self.quantity_entry.delete(0, tk.END)
            self.profit_preview.config(text="$0.00")
    
    def update_profit_preview(self, event=None):
        # Calculate profit preview for the sale
        try:
            product_name = self.product_select.get()
            if product_name in self.product_list:
                cost = self.product_list[product_name].get('cost_price', 0)
                selling = float(self.selling_price_entry.get().strip()) if self.selling_price_entry.get().strip() else 0
                quantity = float(self.quantity_entry.get().strip()) if self.quantity_entry.get().strip() else 0
                
                profit = quantity * (selling - cost)
                self.profit_preview.config(text=f"${profit:,.2f}")
                
                # Color code profit
                if profit > 0:
                    self.profit_preview.config(fg='#27AE60')
                elif profit < 0:
                    self.profit_preview.config(fg='#E74C3C')
                else:
                    self.profit_preview.config(fg='#7F8C8D')
            else:
                self.profit_preview.config(text="$0.00")
        except:
            self.profit_preview.config(text="$0.00")
    
    def record_sale(self):
        # Record a sale in the database
        product_name = self.product_select.get()
        selling_price_str = self.selling_price_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        
        # Validation
        if not product_name:
            messagebox.showerror("Error", "Please select a product")
            return
        
        if not selling_price_str:
            messagebox.showerror("Error", "Please enter selling price")
            return
        
        if not quantity_str:
            messagebox.showerror("Error", "Please enter quantity sold")
            return
        
        try:
            selling_price = float(selling_price_str)
            quantity = float(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        
        if selling_price <= 0:
            messagebox.showerror("Error", "Selling price must be greater than 0")
            return
        
        # Record the sale
        success, message = record_sale(product_name, quantity, selling_price)
        
        if success:
            messagebox.showinfo("Success", message)
            
            # Clear form after successful sale
            self.quantity_entry.delete(0, tk.END)
            self.selling_price_entry.delete(0, tk.END)
            self.profit_preview.config(text="$0.00")
            
            # Refresh product list and sales display
            self.load_products()
            self.load_today_sales()
            
            # Refresh dashboard if callback exists
            if self.refresh_callback:
                self.refresh_callback()
            
            # Clear product selection
            self.product_select.set('')
            self.available_label.config(text="0 KG")
            self.cost_label.config(text="$0.00")
        else:
            messagebox.showerror("Error", message)
    
    def load_today_sales(self):
        # Load today's sales into the table
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        sales = get_today_sales()
        
        total_quantity = 0
        total_profit = 0
        
        for sale in sales:
            self.sales_tree.insert('', 'end', values=(
                sale['product_name'],
                f"{sale['quantity_sold']:.2f} KG",
                f"${sale['selling_price']:.2f}",
                f"${sale['cost_price']:.2f}",
                f"${sale['profit']:.2f}",
                sale['timestamp'].strftime('%H:%M')
            ))
            total_quantity += sale['quantity_sold']
            total_profit += sale['profit']
        
        # Update summary labels
        self.total_sales_label.config(text=f"Today's Total Sales: {total_quantity:.2f} KG")
        self.total_profit_label.config(text=f"Today's Total Profit: ${total_profit:.2f}")