#imports tkinter and db file for mongo storage
import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    create_supermarket_product, 
    get_all_supermarket_products, 
    update_supermarket_product, 
    delete_supermarket_product,
    search_supermarket_products
)

class SupermarketProducts(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="SUPERMARKET PRODUCTS MANAGEMENT", 
                font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Add Product Form
        form_frame = tk.LabelFrame(self, text="ADD NEW PRODUCT", 
                                   font=("Segoe UI", 11, "bold"), 
                                   bg='#FFFFFF', fg='#E67E22')
        form_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(pady=15, padx=15)
        
        tk.Label(form_inner, text="Product Name:", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_name = tk.Entry(form_inner, width=25, font=("Segoe UI", 10), 
                                      relief='solid', bd=1)
        self.product_name.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_inner, text="Quantity (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.product_qty = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), 
                                     relief='solid', bd=1)
        self.product_qty.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(form_inner, text="Price per KG ($):", font=("Segoe UI", 10), 
                bg='#FFFFFF').grid(row=0, column=4, padx=10, pady=10, sticky='w')
        self.product_price = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), 
                                       relief='solid', bd=1)
        self.product_price.grid(row=0, column=5, padx=10, pady=10)
        
        tk.Label(form_inner, text="Total Value:", font=("Segoe UI", 10, "bold"), 
                bg='#FFFFFF', fg='#E67E22').grid(row=0, column=6, padx=10, pady=10, sticky='w')
        self.total_label = tk.Label(form_inner, text="$0.00", font=("Segoe UI", 10, "bold"), 
                                     bg='#FFFFFF', fg='#27AE60')
        self.total_label.grid(row=0, column=7, padx=10, pady=10)
        
        self.product_qty.bind('<KeyRelease>', self.calculate_total)
        self.product_price.bind('<KeyRelease>', self.calculate_total)
        
        tk.Button(form_inner, text="ADD PRODUCT", command=self.add_product,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).grid(row=1, column=0, columnspan=8, pady=15)
        
        # Search Bar
        search_frame = tk.Frame(self, bg='#FFFFFF')
        search_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), 
                bg='#FFFFFF').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 10), 
                                      relief='solid', bd=1)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(search_frame, text="SEARCH", command=self.search_products,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        tk.Button(search_frame, text="SHOW ALL", command=self.load_products,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 9), 
                 relief='flat', padx=15).pack(side='left', padx=5)
        
        # Products Table
        table_frame = tk.Frame(self, bg='#FFFFFF', relief='solid', bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)
        
        columns = ('Name', 'Quantity (KG)', 'Price per KG', 'Total Value')
        self.product_tree = ttk.Treeview(table_frame, columns=columns, 
                                          show='headings', height=15)
        
        self.product_tree.heading('Name', text='Product Name')
        self.product_tree.heading('Quantity (KG)', text='Quantity (KG)')
        self.product_tree.heading('Price per KG', text='Price per KG ($)')
        self.product_tree.heading('Total Value', text='Total Value ($)')
        
        self.product_tree.column('Name', width=250)
        self.product_tree.column('Quantity (KG)', width=150)
        self.product_tree.column('Price per KG', width=150)
        self.product_tree.column('Total Value', width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                  command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        btn_frame = tk.Frame(self, bg='#F5F6FA')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="EDIT SELECTED", command=self.edit_product,
                 bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="DELETE SELECTED", command=self.delete_product,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
    
    def calculate_total(self, event=None):
        """Calculate total value: Quantity (KG) × Price per KG"""
        try:
            qty = self.product_qty.get().strip()
            price = self.product_price.get().strip()
            
            if qty and price:
                qty_float = float(qty)
                price_float = float(price)
                total = qty_float * price_float
                self.total_label.config(text=f"${total:,.2f}")
            else:
                self.total_label.config(text="$0.00")
        except ValueError:
            self.total_label.config(text="$0.00")
    
    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        products = get_all_supermarket_products()
        
        for p in products:
            total = p['quantity'] * p['price']
            self.product_tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:,.2f} KG",
                f"${p['price']:,.2f}",
                f"${total:,.2f}"
            ), tags=(p['name'],))
    
    def search_products(self):
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            self.load_products()
            return
        
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        products = search_supermarket_products(keyword)
        
        for p in products:
            total = p['quantity'] * p['price']
            self.product_tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:,.2f} KG",
                f"${p['price']:,.2f}",
                f"${total:,.2f}"
            ), tags=(p['name'],))
    
    def add_product(self):
        name = self.product_name.get().strip()
        qty = self.product_qty.get().strip()
        price = self.product_price.get().strip()
        
        if not name or not qty or not price:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            qty = float(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be valid numbers")
            return
        
        success, message = create_supermarket_product(name, qty, price)
        
        if success:
            messagebox.showinfo("Success", message)
            self.product_name.delete(0, tk.END)
            self.product_qty.delete(0, tk.END)
            self.product_price.delete(0, tk.END)
            self.total_label.config(text="$0.00")
            self.load_products()
        else:
            messagebox.showerror("Error", message)
    
    def edit_product(self):
        selected = self.product_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a product to edit")
            return
        
        values = self.product_tree.item(selected[0])['values']
        product_name = values[0]
        current_qty = float(values[1].replace(' KG', '').replace(',', ''))
        current_price = float(values[2].replace('$', '').replace(',', ''))
        
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Product")
        edit_window.geometry("450x350")
        edit_window.configure(bg='#FFFFFF')
        edit_window.resizable(False, False)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() - 450) // 2
        y = (edit_window.winfo_screenheight() - 350) // 2
        edit_window.geometry(f'450x350+{x}+{y}')
        
        tk.Label(edit_window, text="EDIT PRODUCT", font=("Segoe UI", 14, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        tk.Label(edit_window, text="Product Name:", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        name_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                              relief='solid', bd=1)
        name_entry.insert(0, product_name)
        name_entry.config(state='readonly')
        name_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Quantity (KG):", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        qty_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                             relief='solid', bd=1)
        qty_entry.insert(0, current_qty)
        qty_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Price per KG ($):", font=("Segoe UI", 10), 
                bg='#FFFFFF').pack(pady=5)
        price_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), 
                               relief='solid', bd=1)
        price_entry.insert(0, current_price)
        price_entry.pack(pady=5)
        
        total_display_label = tk.Label(edit_window, text="", font=("Segoe UI", 11, "bold"), 
                                        bg='#FFFFFF', fg='#27AE60')
        total_display_label.pack(pady=5)
        
        def update_edit_total(event=None):
            try:
                qty = float(qty_entry.get().strip()) if qty_entry.get().strip() else 0
                price = float(price_entry.get().strip()) if price_entry.get().strip() else 0
                total = qty * price
                total_display_label.config(text=f"Total Value: ${total:,.2f}")
            except:
                total_display_label.config(text="Total Value: $0.00")
        
        qty_entry.bind('<KeyRelease>', update_edit_total)
        price_entry.bind('<KeyRelease>', update_edit_total)
        update_edit_total()
        
        def save_changes():
            try:
                new_qty = float(qty_entry.get().strip())
                new_price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity or price")
                return
            
            success, message = update_supermarket_product(product_name, new_qty, new_price)
            
            if success:
                messagebox.showinfo("Success", message)
                edit_window.destroy()
                self.load_products()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(edit_window, text="SAVE CHANGES", command=save_changes,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(pady=20)
    
    def delete_product(self):
        selected = self.product_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a product to delete")
            return
        
        values = self.product_tree.item(selected[0])['values']
        product_name = values[0]
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Are you sure you want to delete '{product_name}'? This will affect all supermarket admins."):
            
            success, message = delete_supermarket_product(product_name)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_products()
            else:
                messagebox.showerror("Error", message)