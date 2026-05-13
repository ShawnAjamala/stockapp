## imports tkinter for gui and db for mongo storage
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
    #Main class for warehouse stock management interface#
    
    def __init__(self, parent, user):
        #Initialize the warehouse stock frame
        #parent: The parent widget (main_content frame)
        #user: The logged in user object (contains email, fullname, role)
        super().__init__(parent)
        self.user = user
        self.configure(bg='#F5F6FA')
        
        # Create all UI elements
        self.create_widgets()
        
        # Load existing stock from database
        self.load_stock()
    
    def create_widgets(self):
        """Create all UI elements for the warehouse stock page"""
        
        # HEADER SECTION
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="WAREHOUSE STOCK MANAGEMENT", 
                font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # ==================== ADD STOCK FORM ====================
        # This form allows warehouse admins to add new products to warehouse inventory
        form_frame = tk.LabelFrame(self, text="ADD NEW STOCK", 
                                   font=("Segoe UI", 11, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        form_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(pady=15, padx=15)
        
        # Product Name input field
        tk.Label(form_inner, text="Product Name:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_name = tk.Entry(form_inner, width=25, font=("Segoe UI", 10), 
                                      relief='solid', bd=1)
        self.product_name.grid(row=0, column=1, padx=10, pady=10)
        
        # Quantity in KG input field
        tk.Label(form_inner, text="Quantity (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.product_qty = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), 
                                     relief='solid', bd=1)
        self.product_qty.grid(row=0, column=3, padx=10, pady=10)
        
        # Price per KG input field
        tk.Label(form_inner, text="Price per KG ($):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=4, padx=10, pady=10, sticky='w')
        self.product_price = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), 
                                       relief='solid', bd=1)
        self.product_price.grid(row=0, column=5, padx=10, pady=10)
        
        # Display calculated total
        tk.Label(form_inner, text="Total Value:", font=("Segoe UI", 10, "bold"), 
                bg='#FFFFFF', fg='#E67E22').grid(row=0, column=6, padx=10, pady=10, sticky='w')
        self.total_label = tk.Label(form_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                     bg='#FFFFFF', fg='#27AE60')
        self.total_label.grid(row=0, column=7, padx=10, pady=10)
        
        # Bind events to calculate total automatically when quantity or price changes
        self.product_qty.bind('<KeyRelease>', self.calculate_total)
        self.product_price.bind('<KeyRelease>', self.calculate_total)
        
        # Add Stock button - calls add_stock method
        tk.Button(form_inner, text="ADD STOCK", command=self.add_stock,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).grid(row=1, column=0, columnspan=8, pady=15)
        
        # SEARCH BAR 
        search_frame = tk.Frame(self, bg='#FFFFFF')
        search_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), 
                bg='#FFFFFF').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 10), 
                                      relief='solid', bd=1)
        self.search_entry.pack(side='left', padx=5)
        
        # Search button - filters products by name
        tk.Button(search_frame, text="SEARCH", command=self.search_stock,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        # Show All button - clears search and shows all products
        tk.Button(search_frame, text="SHOW ALL", command=self.load_stock,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        #  STOCK TABLE-Displays all warehouse products in a table format
        table_frame = tk.Frame(self, bg='#FFFFFF', relief='solid', bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)
        
        # Define table columns - now shows Price per KG instead of just Price
        columns = ('Name', 'Quantity (KG)', 'Price per KG', 'Total Value')
        self.stock_tree = ttk.Treeview(table_frame, columns=columns, 
                                        show='headings', height=15)
        
        # Configure column headings and widths
        self.stock_tree.heading('Name', text='Product Name')
        self.stock_tree.heading('Quantity (KG)', text='Quantity (KG)')
        self.stock_tree.heading('Price per KG', text='Price per KG ($)')
        self.stock_tree.heading('Total Value', text='Total Value ($)')
        
        self.stock_tree.column('Name', width=250)
        self.stock_tree.column('Quantity (KG)', width=150)
        self.stock_tree.column('Price per KG', width=150)
        self.stock_tree.column('Total Value', width=150)
        
        # Add scrollbar for the table
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                  command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the table and scrollbar
        self.stock_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # ACTION BUTTONS =Buttons for editing and deleting selected products
        btn_frame = tk.Frame(self, bg='#F5F6FA')
        btn_frame.pack(pady=15)
        
        # Edit button - opens edit window for selected product
        tk.Button(btn_frame, text="EDIT SELECTED", command=self.edit_stock,
                 bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
        
        # Delete button - removes selected product after confirmation
        tk.Button(btn_frame, text="DELETE SELECTED", command=self.delete_stock,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
    
    def calculate_total(self, event=None):
        """
        Calculate total value based on quantity (KG) and price per KG
        Automatically called when user types in quantity or price fields
        Formula: Total = Quantity (KG) × Price per KG
        """
        try:
            # Get quantity and price values
            qty = self.product_qty.get().strip()
            price = self.product_price.get().strip()
            
            # Calculate if both fields have valid numbers
            if qty and price:
                qty_float = float(qty)
                price_float = float(price)
                total = qty_float * price_float
                # Update the total label with formatted currency
                self.total_label.config(text=f"${total:,.2f}")
            else:
                # Reset if fields are empty
                self.total_label.config(text="$0.00")
        except ValueError:
            # Handle invalid input
            self.total_label.config(text="$0.00")
    
    def load_stock(self):
        """
        Load ALL warehouse products from MongoDB
        No user_email filter - all warehouse admins see the same data
        """
        # Clear existing items from the table
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Fetch all warehouse products from database (type: "warehouse")
        products = get_all_warehouse_products()
        
        # Insert each product into the table
        for p in products:
            # Calculate total value (quantity * price per KG)
            total = p['quantity'] * p['price']
            
            # Insert product row with formatted values
            self.stock_tree.insert('', 'end', values=(
                p['name'],                    # Product name
                f"{p['quantity']:,.2f} KG",   # Quantity with KG unit
                f"${p['price']:,.2f}",        # Price per KG formatted as currency
                f"${total:,.2f}"              # Total value formatted as currency
            ), tags=(p['name'],))
    
    def search_stock(self):
        """
        Search warehouse products by name
        Filters products based on user input in search box
        """
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            self.load_stock()
            return
        
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        products = search_warehouse_products(keyword)
        
        for p in products:
            total = p['quantity'] * p['price']
            self.stock_tree.insert('', 'end', values=(
                p['name'], 
                f"{p['quantity']:,.2f} KG",
                f"${p['price']:,.2f}", 
                f"${total:,.2f}"
            ), tags=(p['name'],))
    
    def add_stock(self):
        """
        Add new product to warehouse inventory
        Price is stored as price per KG
        Total value is calculated as Quantity × Price per KG
        """
        name = self.product_name.get().strip()
        qty = self.product_qty.get().strip()
        price = self.product_price.get().strip()
        
        if not name or not qty or not price:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            qty = float(qty)  # Allow decimal quantities for KG
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be valid numbers")
            return
        
        # Call database function to create product
        success, message = create_warehouse_product(name, qty, price)
        
        if success:
            messagebox.showinfo("Success", message)
            
            # Clear form fields
            self.product_name.delete(0, tk.END)
            self.product_qty.delete(0, tk.END)
            self.product_price.delete(0, tk.END)
            self.total_label.config(text="$0.00")
            
            self.load_stock()
        else:
            messagebox.showerror("Error", message)
    
    def edit_stock(self):
        """
        Edit selected warehouse product
        Opens a popup window to modify quantity (KG) and price per KG
        Total is recalculated automatically
        """
        selected = self.stock_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select an item to edit")
            return
        
        values = self.stock_tree.item(selected[0])['values']
        product_name = values[0]
        # Extract numeric values (remove units and $ symbols)
        current_qty = float(values[1].replace(' KG', '').replace(',', ''))
        current_price = float(values[2].replace('$', '').replace(',', ''))
        
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Stock")
        edit_window.geometry("450x350")
        edit_window.configure(bg='#FFFFFF')
        edit_window.resizable(False, False)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() - 450) // 2
        y = (edit_window.winfo_screenheight() - 350) // 2
        edit_window.geometry(f'450x350+{x}+{y}')
        
        tk.Label(edit_window, text="EDIT STOCK", font=("Segoe UI", 14, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Product Name (readonly)
        tk.Label(edit_window, text="Product Name:", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        name_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                              relief='solid', bd=1)
        name_entry.insert(0, product_name)
        name_entry.config(state='readonly')
        name_entry.pack(pady=5)
        
        # Quantity in KG
        tk.Label(edit_window, text="Quantity (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        qty_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                             relief='solid', bd=1)
        qty_entry.insert(0, current_qty)
        qty_entry.pack(pady=5)
        
        # Price per KG
        tk.Label(edit_window, text="Price per KG ($):", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        price_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                               relief='solid', bd=1)
        price_entry.insert(0, current_price)
        price_entry.pack(pady=5)
        
        # Live total display during editing
        total_display_label = tk.Label(edit_window, text="", font=("Segoe UI", 11, "bold"), 
                                        bg='#FFFFFF', fg='#27AE60')
        total_display_label.pack(pady=5)
        
        def update_edit_total(event=None):
            """Update total display in edit window"""
            try:
                qty = float(qty_entry.get().strip()) if qty_entry.get().strip() else 0
                price = float(price_entry.get().strip()) if price_entry.get().strip() else 0
                total = qty * price
                total_display_label.config(text=f"Total Value: ${total:,.2f}")
            except:
                total_display_label.config(text="Total Value: $0.00")
        
        # Bind events to update total
        qty_entry.bind('<KeyRelease>', update_edit_total)
        price_entry.bind('<KeyRelease>', update_edit_total)
        update_edit_total()  # Initial calculation
        
        def save_changes():
            try:
                new_qty = float(qty_entry.get().strip())
                new_price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity or price")
                return
            
            success, message = update_warehouse_product(product_name, new_qty, new_price)
            
            if success:
                messagebox.showinfo("Success", message)
                edit_window.destroy()
                self.load_stock()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(edit_window, text="SAVE CHANGES", command=save_changes,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(pady=20)
    
    def delete_stock(self):
        selected = self.stock_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select an item to delete")
            return
        
        values = self.stock_tree.item(selected[0])['values']
        product_name = values[0]
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Are you sure you want to delete '{product_name}'? This will affect all warehouse admins."):
            
            success, message = delete_warehouse_product(product_name)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_stock()
            else:
                messagebox.showerror("Error", message)