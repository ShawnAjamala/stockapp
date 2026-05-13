import tkinter as tk
from tkinter import ttk, messagebox

class SupermarketProducts(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.parent = parent
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="PRODUCT MANAGEMENT", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Add Product Form
        form_frame = tk.LabelFrame(self, text="ADD NEW PRODUCT", 
                                   font=("Segoe UI", 11, "bold"), bg='#FFFFFF', fg='#E67E22')
        form_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        form_inner = tk.Frame(form_frame, bg='#FFFFFF')
        form_inner.pack(pady=15, padx=15)
        
        tk.Label(form_inner, text="Product Name:", font=("Segoe UI", 10), bg='#FFFFFF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_name = tk.Entry(form_inner, width=25, font=("Segoe UI", 10), relief='solid', bd=1)
        self.product_name.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_inner, text="Quantity:", font=("Segoe UI", 10), bg='#FFFFFF').grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.product_qty = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.product_qty.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(form_inner, text="Price ($):", font=("Segoe UI", 10), bg='#FFFFFF').grid(row=0, column=4, padx=10, pady=10, sticky='w')
        self.product_price = tk.Entry(form_inner, width=15, font=("Segoe UI", 10), relief='solid', bd=1)
        self.product_price.grid(row=0, column=5, padx=10, pady=10)
        
        tk.Button(form_inner, text="ADD PRODUCT", command=self.add_product,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).grid(row=0, column=6, padx=10, pady=10)
        
        # Search Bar
        search_frame = tk.Frame(self, bg='#FFFFFF')
        search_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), bg='#FFFFFF').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="SEARCH", command=self.search_products,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9), relief='flat', padx=15).pack(side='left', padx=5)
        tk.Button(search_frame, text="SHOW ALL", command=self.load_products,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 9), relief='flat', padx=15).pack(side='left', padx=5)
        
        # Products Table
        table_frame = tk.Frame(self, bg='#FFFFFF', relief='solid', bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)
        
        columns = ('Name', 'Quantity', 'Price', 'Total Value')
        self.product_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=180)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Buttons for actions
        btn_frame = tk.Frame(self, bg='#F5F6FA')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="EDIT SELECTED", command=self.edit_product,
                 bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="DELETE SELECTED", command=self.delete_product,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
    
    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        sample_products = [
            {"name": "Rice 1kg", "quantity": 50, "price": 120},
            {"name": "Cooking Oil 2L", "quantity": 30, "price": 350},
            {"name": "Sugar 1kg", "quantity": 100, "price": 90},
        ]
        
        for p in sample_products:
            total = p['quantity'] * p['price']
            self.product_tree.insert('', 'end', values=(
                p['name'], p['quantity'], f"${p['price']:.2f}", f"${total:.2f}"
            ))
    
    def search_products(self):
        keyword = self.search_entry.get().lower()
        if not keyword:
            self.load_products()
            return
        
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        sample_products = [
            {"name": "Rice 1kg", "quantity": 50, "price": 120},
            {"name": "Cooking Oil 2L", "quantity": 30, "price": 350},
            {"name": "Sugar 1kg", "quantity": 100, "price": 90},
        ]
        
        for p in sample_products:
            if keyword in p['name'].lower():
                total = p['quantity'] * p['price']
                self.product_tree.insert('', 'end', values=(
                    p['name'], p['quantity'], f"${p['price']:.2f}", f"${total:.2f}"
                ))
    
    def add_product(self):
        name = self.product_name.get().strip()
        qty = self.product_qty.get().strip()
        price = self.product_price.get().strip()
        
        if not name or not qty or not price:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            qty = int(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number and price must be a valid amount")
            return
        
        total = qty * price
        self.product_tree.insert('', 'end', values=(name, qty, f"${price:.2f}", f"${total:.2f}"))
        
        self.product_name.delete(0, tk.END)
        self.product_qty.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Product '{name}' added successfully!")
    
    def edit_product(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to edit")
            return
        
        values = self.product_tree.item(selected[0])['values']
        
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Product")
        edit_window.geometry("400x300")
        edit_window.configure(bg='#FFFFFF')
        edit_window.resizable(False, False)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() - 400) // 2
        y = (edit_window.winfo_screenheight() - 300) // 2
        edit_window.geometry(f'400x300+{x}+{y}')
        
        tk.Label(edit_window, text="EDIT PRODUCT", font=("Segoe UI", 14, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        tk.Label(edit_window, text="Product Name:", font=("Segoe UI", 10), bg='#FFFFFF').pack(pady=5)
        name_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        name_entry.insert(0, values[0])
        name_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Quantity:", font=("Segoe UI", 10), bg='#FFFFFF').pack(pady=5)
        qty_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        qty_entry.insert(0, values[1])
        qty_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Price ($):", font=("Segoe UI", 10), bg='#FFFFFF').pack(pady=5)
        price_entry = tk.Entry(edit_window, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        price_entry.insert(0, values[2].replace('$', ''))
        price_entry.pack(pady=5)
        
        def save_changes():
            new_name = name_entry.get().strip()
            new_qty = int(qty_entry.get().strip())
            new_price = float(price_entry.get().strip())
            new_total = new_qty * new_price
            
            self.product_tree.item(selected[0], values=(new_name, new_qty, f"${new_price:.2f}", f"${new_total:.2f}"))
            messagebox.showinfo("Success", "Product updated successfully!")
            edit_window.destroy()
        
        tk.Button(edit_window, text="SAVE CHANGES", command=save_changes,
                 bg='#27AE60', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(pady=20)
    
    def delete_product(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            self.product_tree.delete(selected[0])
            messagebox.showinfo("Success", "Product deleted successfully!")