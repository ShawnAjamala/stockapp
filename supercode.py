## supermarket code
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SupermarketDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"FreshStock Manager - Supermarket Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg='#F5F6FA')
        
        self.products = []
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1200) // 2
        y = (self.root.winfo_screenheight() - 700) // 2
        self.root.geometry(f'1200x700+{x}+{y}')
    
    def create_widgets(self):
        # Top Navigation Bar
        nav_bar = tk.Frame(self.root, bg='#E67E22', height=65)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)
        
        # Logo section
        logo_frame = tk.Frame(nav_bar, bg='#E67E22')
        logo_frame.pack(side='left', padx=30, pady=12)
        
        tk.Label(logo_frame, text="FRESHSTOCK", font=("Segoe UI", 18, "bold"), bg='#E67E22', fg='white').pack(side='left')
        tk.Label(logo_frame, text="Supermarket", font=("Segoe UI", 10), bg='#E67E22', fg='#FAD7A1').pack(side='left', padx=(8,0))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Receive Stock", self.show_receive),
            ("Transfers", self.show_transfers),
            ("Profile", self.show_profile)
        ]
        
        nav_frame = tk.Frame(nav_bar, bg='#E67E22')
        nav_frame.pack(side='left', padx=50)
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                          bg='#E67E22', fg='white', font=("Segoe UI", 10),
                          relief='flat', cursor='hand2', padx=20, pady=8)
            btn.pack(side='left', padx=5)
            
            def on_enter(e, b=btn): b.configure(bg='#D35400')
            def on_leave(e, b=btn): b.configure(bg='#E67E22')
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Logout button
        logout_btn = tk.Button(nav_bar, text="LOGOUT", command=self.logout,
                              bg='#C0392B', fg='white', font=("Segoe UI", 10, "bold"),
                              relief='flat', cursor='hand2', padx=25, pady=8)
        logout_btn.pack(side='right', padx=30)
        
        # Main content area
        self.main_content = tk.Frame(self.root, bg='#F5F6FA')
        self.main_content.pack(fill="both", expand=True, padx=25, pady=20)
        
        self.show_dashboard()
    
    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Hero Section
        hero_frame = tk.Frame(self.main_content, bg='#FFFFFF', relief='flat')
        hero_frame.pack(fill="x", pady=(0, 20))
        
        hero_bg = tk.Frame(hero_frame, bg='#E67E22', height=160)
        hero_bg.pack(fill="x")
        hero_bg.pack_propagate(False)
        
        hero_content = tk.Frame(hero_bg, bg='#E67E22')
        hero_content.pack(expand=True, pady=25)
        
        tk.Label(hero_content, text="WELCOME BACK", font=("Segoe UI", 11), 
                bg='#E67E22', fg='#FAD7A1').pack()
        tk.Label(hero_content, text=f"{self.user['fullname']}", font=("Segoe UI", 26, "bold"), 
                bg='#E67E22', fg='white').pack()
        tk.Label(hero_content, text="Supermarket Administrator Dashboard", font=("Segoe UI", 11), 
                bg='#E67E22', fg='#FAD7A1').pack()
        
        # Stats Cards
        stats_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        stats_frame.pack(fill="x", pady=20)
        
        # Card 1
        card1 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card1.pack(side='left', padx=10, fill='x', expand=True)
        card1.pack_propagate(False)
        tk.Label(card1, text="PRODUCTS", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card1, text="0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 2
        card2 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card2.pack(side='left', padx=10, fill='x', expand=True)
        card2.pack_propagate(False)
        tk.Label(card2, text="PENDING TRANSFERS", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card2, text="0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 3
        card3 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card3.pack(side='left', padx=10, fill='x', expand=True)
        card3.pack_propagate(False)
        tk.Label(card3, text="INVENTORY VALUE", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card3, text="$0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Recent Activity
        activity_frame = tk.Frame(self.main_content, bg='#FFFFFF', relief='flat', bd=1)
        activity_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(activity_frame, text="RECENT ACTIVITY", font=("Segoe UI", 12, "bold"), 
                bg='#FFFFFF', fg='#2C3E50').pack(anchor='w', padx=20, pady=15)
        
        activity_text = tk.Text(activity_frame, height=8, bg='#F8F9FA', fg='#5D4E37', 
                               font=("Segoe UI", 10), relief='flat')
        activity_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        activity_text.insert('1.0', "No recent activity yet\nUse the navigation menu to manage your inventory")
        activity_text.configure(state='disabled')
    
    def show_products(self):
        self.clear_content()
        
        # Header
        header_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="PRODUCT MANAGEMENT", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Add Product Form
        form_frame = tk.LabelFrame(self.main_content, text="ADD NEW PRODUCT", 
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
        search_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        search_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), bg='#FFFFFF').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 10), relief='solid', bd=1)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="SEARCH", command=self.search_products,
                 bg='#3498DB', fg='white', font=("Segoe UI", 9), relief='flat', padx=15).pack(side='left', padx=5)
        tk.Button(search_frame, text="SHOW ALL", command=self.load_products,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 9), relief='flat', padx=15).pack(side='left', padx=5)
        
        # Products Table
        table_frame = tk.Frame(self.main_content, bg='#FFFFFF', relief='solid', bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)
        
        # Create Treeview
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
        btn_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="EDIT SELECTED", command=self.edit_product,
                 bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="DELETE SELECTED", command=self.delete_product,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(side='left', padx=10)
        
        self.load_products()
    
    def show_receive(self):
        self.clear_content()
        
        header_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="RECEIVE STOCK FROM WAREHOUSE", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        content_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        content_frame.pack(fill="both", expand=True)
        
        tk.Label(content_frame, text="Receive Stock Feature", font=("Segoe UI", 14), 
                bg='#FFFFFF', fg='#7F8C8D').pack(expand=True)
        tk.Label(content_frame, text="Coming Soon in Phase 3", font=("Segoe UI", 11), 
                bg='#FFFFFF', fg='#95A5A6').pack()
    
    def show_transfers(self):
        self.clear_content()
        
        header_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="TRANSFER HISTORY", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        content_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        content_frame.pack(fill="both", expand=True)
        
        tk.Label(content_frame, text="Transfer History Feature", font=("Segoe UI", 14), 
                bg='#FFFFFF', fg='#7F8C8D').pack(expand=True)
        tk.Label(content_frame, text="Coming Soon in Phase 3", font=("Segoe UI", 11), 
                bg='#FFFFFF', fg='#95A5A6').pack()
    
    def show_profile(self):
        self.clear_content()
        
        header_frame = tk.Frame(self.main_content, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="MY PROFILE", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        # Profile Card
        profile_card = tk.Frame(self.main_content, bg='#FFFFFF', relief='raised', bd=1)
        profile_card.pack(pady=20, padx=100, fill="both", expand=True)
        
        details_frame = tk.Frame(profile_card, bg='#FFFFFF')
        details_frame.pack(pady=40, padx=50)
        
        tk.Label(details_frame, text="USER INFORMATION", font=("Segoe UI", 16, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=(0, 25))
        
        fields = [
            ("Full Name:", self.user['fullname']),
            ("Email Address:", self.user['email']),
            ("Role:", self.user['role'].upper()),
            ("Account Type:", "Supermarket Administrator")
        ]
        
        for label, value in fields:
            row_frame = tk.Frame(details_frame, bg='#FFFFFF')
            row_frame.pack(fill='x', pady=12)
            tk.Label(row_frame, text=label, font=("Segoe UI", 11, "bold"), 
                    bg='#FFFFFF', fg='#2C3E50', width=18, anchor='w').pack(side='left')
            tk.Label(row_frame, text=value, font=("Segoe UI", 11), 
                    bg='#FFFFFF', fg='#5D4E37', anchor='w').pack(side='left', padx=(15, 0))
        
        # Action Buttons
        btn_frame = tk.Frame(profile_card, bg='#FFFFFF')
        btn_frame.pack(pady=25)
        
        tk.Button(btn_frame, text="DELETE ACCOUNT", command=self.delete_account,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=30, pady=8).pack(side='left', padx=10)
    
    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Sample data for demo
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
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Product")
        edit_window.geometry("400x300")
        edit_window.configure(bg='#FFFFFF')
        edit_window.resizable(False, False)
        
        # Center edit window
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
    
    def delete_account(self):
        if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account? This action cannot be undone!"):
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully")
            self.logout()
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from auth import AuthWindow
            root = tk.Tk()
            AuthWindow(root)
            root.mainloop()


            