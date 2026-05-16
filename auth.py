# Imports the necessary requirements from tkinter for the GUI
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from supermarket_dashboard import SupermarketDashboard
from warehouse_dashboard import WarehouseDashboard
from db import (
    create_user, find_user_by_email, find_user_by_email_and_password,
    SUPERMARKET_PASSWORD, WAREHOUSE_PASSWORD
)

# This is where the authentication page is made using tkinter for GUI
class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FreshStock Manager - Login")
        self.root.geometry("450x500")
        self.root.configure(bg='#FFF8F0')
        
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f'450x500+{x}+{y}')
    
    def create_widgets(self):
        """Create all GUI elements"""
        # Header
        header = tk.Frame(self.root, bg='#E67E22', height=100)
        header.pack(fill="x")
        tk.Label(header, text="FRESHSTOCK MANAGER", 
                font=("Arial", 14, "bold"), bg='#E67E22', fg='white').pack(pady=35)
        
        # Tabs
        style = ttk.Style()
        style.configure('TNotebook', background='#FFF8F0')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Login tab
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="LOGIN")
        self.create_login_tab(login_frame)
        
        # Register tab
        register_frame = ttk.Frame(notebook)
        notebook.add(register_frame, text="REGISTER")
        self.create_register_tab(register_frame)
    
    def create_login_tab(self, parent):
       #Creates Login form
        container = tk.Frame(parent, bg='#FFFFFF')
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(container, text="Welcome Back", font=("Arial", 12, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=(0, 20))
        
        # Email
        tk.Label(container, text="Email:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.login_email = tk.Entry(container, width=30, bg='#FFF8F0', fg='#5D4E37', relief='solid', bd=1)
        self.login_email.pack(fill="x", pady=(0, 15))
        self.login_email.bind('<Return>', lambda e: self.login())
        
        # Password
        tk.Label(container, text="Password:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.login_password = tk.Entry(container, show="*", width=30, bg='#FFF8F0', fg='#5D4E37', relief='solid', bd=1)
        self.login_password.pack(fill="x", pady=(0, 20))
        self.login_password.bind('<Return>', lambda e: self.login())
        
        # Login button
        tk.Button(container, text="LOGIN", command=self.login,
                 bg='#E67E22', fg='white', font=("Arial", 10, "bold"), relief='flat').pack(fill="x")
    
    def create_register_tab(self, parent):
        #Creates registration form
        container = tk.Frame(parent, bg='#FFFFFF')
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(container, text="Create Account", font=("Arial", 12, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=(0, 20))
        
        # Full Name
        tk.Label(container, text="Full Name:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.reg_name = tk.Entry(container, width=30, bg='#FFF8F0', fg='#5D4E37', relief='solid', bd=1)
        self.reg_name.pack(fill="x", pady=(0, 10))
        
        # Email
        tk.Label(container, text="Email:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.reg_email = tk.Entry(container, width=30, bg='#FFF8F0', fg='#5D4E37', relief='solid', bd=1)
        self.reg_email.pack(fill="x", pady=(0, 10))
        
        # Role – store simple names without "admin"
        tk.Label(container, text="Role:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.reg_role = ttk.Combobox(container, values=["supermarket", "warehouse"])
        self.reg_role.pack(fill="x", pady=(0, 10))
        
        # Role Password
        tk.Label(container, text="Role Password:", bg='#FFFFFF', fg='#5D4E37').pack(anchor='w')
        self.reg_password = tk.Entry(container, show="*", width=30, bg='#FFF8F0', fg='#5D4E37', relief='solid', bd=1)
        self.reg_password.pack(fill="x", pady=(0, 20))
        
        # Register button
        tk.Button(container, text="REGISTER", command=self.register,
                 bg='#27AE60', fg='white', font=("Arial", 10, "bold"), relief='flat').pack(fill="x")
    
    def login(self):
       ## Handles login process
        email = self.login_email.get().strip()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        # Show loading message
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            user = find_user_by_email_and_password(email, password)
            
            if user:
                messagebox.showinfo("Success", f"Welcome {user['fullname']}!\nRole: {user['role']}")
                self.root.config(cursor="")
                self.root.destroy()
                self.open_dashboard(user)
            else:
                self.root.config(cursor="")
                messagebox.showerror("Error", "Invalid email or password")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Error", f"Connection error: {str(e)}\nPlease check your internet connection")
    
    def register(self):
       # Handles registration process
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        role = self.reg_role.get()
        password = self.reg_password.get()
        
        if not all([name, email, role, password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        #Checks email authenticity
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Invalid email format")
            return
        
        # Show loading message
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Check if email exists
            if find_user_by_email(email):
                self.root.config(cursor="")
                messagebox.showerror("Error", "Email already registered")
                return
            
            # Check role password
            if role == "supermarket" and password != SUPERMARKET_PASSWORD:
                self.root.config(cursor="")
                messagebox.showerror("Error", "Invalid role password")
                return
            elif role == "warehouse" and password != WAREHOUSE_PASSWORD:
                self.root.config(cursor="")
                messagebox.showerror("Error", "Invalid role password")
                return
            
            # Create user
            create_user(email, password, name, role)
            self.root.config(cursor="")
            messagebox.showinfo("Success", f"User {name} registered successfully!")
            
            # Clear fields
            self.reg_name.delete(0, tk.END)
            self.reg_email.delete(0, tk.END)
            self.reg_role.set('')
            self.reg_password.delete(0, tk.END)
            
            # Switch to login tab
            self.root.children['!notebook'].select(0)
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Error", f"Connection error: {str(e)}\nPlease check your internet connection")
    
    def open_dashboard(self, user):
       #redirects to the specific dashboard depending on ones role
        role = user['role']
        # Normalize role: accept both "supermarket" and "supermarket admin", etc.
        if role in ["supermarket", "supermarket admin"]:
            dashboard_root = tk.Tk()
            SupermarketDashboard(dashboard_root, user)
            dashboard_root.mainloop()
        elif role in ["warehouse", "warehouse admin"]:
            dashboard_root = tk.Tk()
            WarehouseDashboard(dashboard_root, user)
            dashboard_root.mainloop()
        else:
            messagebox.showerror("Error", f"Unknown role: {role}")

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()