# Imports the necessary requirements from tkinter for the GUI
import tkinter as tk
from tkinter import ttk, messagebox
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
        
        # Role
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
        
        user = find_user_by_email_and_password(email, password)
        
        if user:
            messagebox.showinfo("Success", f"Welcome {user['fullname']}!\nRole: {user['role']}")
            self.root.destroy()
            self.open_dashboard(user)
        else:
            messagebox.showerror("Error", "Invalid email or password")
    
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
        
        # Check if email exists
        if find_user_by_email(email):
            messagebox.showerror("Error", "Email already registered")
            return
        
        # Check role password (passwords are to be given by the main admin who made the site)
        if role == "supermarket" and password != SUPERMARKET_PASSWORD:
            messagebox.showerror("Error", "Invalid role password")
            return
        elif role == "warehouse" and password != WAREHOUSE_PASSWORD:
            messagebox.showerror("Error", "Invalid role password")
            return
        
        # Create user
        create_user(email, password, name, role)
        messagebox.showinfo("Success", f"User {name} registered successfully!")
        
        # Clear fields
        self.reg_name.delete(0, tk.END)
        self.reg_email.delete(0, tk.END)
        self.reg_role.set('')
        self.reg_password.delete(0, tk.END)
        
        # Switch to login tab
        self.root.children['!notebook'].select(0)
    
    def open_dashboard(self, user):
       #redirects to the specific dashboard depending on ones role
        dashboard = tk.Tk()
        dashboard.title(f"{user['role'].upper()} Dashboard")
        dashboard.geometry("600x400")
        dashboard.configure(bg='#FFF8F0')
        
        # Center dashboard
        dashboard.update_idletasks()
        x = (dashboard.winfo_screenwidth() - 600) // 2
        y = (dashboard.winfo_screenheight() - 400) // 2
        dashboard.geometry(f'600x400+{x}+{y}')
        
        # Header
        header = tk.Frame(dashboard, bg='#E67E22', height=80)
        header.pack(fill="x")
        tk.Label(header, text=f"{user['role'].upper()} ADMIN DASHBOARD", 
                font=("Arial", 14, "bold"), bg='#E67E22', fg='white').pack(pady=25)
        
        # Content
        content = tk.Frame(dashboard, bg='#FFF8F0')
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(content, text=f"Welcome {user['fullname']}!", 
                font=("Arial", 12, "bold"), bg='#FFF8F0', fg='#E67E22').pack(pady=10)
        tk.Label(content, text=f"Email: {user['email']}\nRole: {user['role']}", 
                bg='#FFF8F0', fg='#5D4E37').pack(pady=5)
        
        # Role-specific info
        if user['role'] == 'supermarket':
            tk.Label(content, text="\nSupermarket Functions:", 
                    font=("Arial", 10, "bold"), bg='#FFF8F0', fg='#E67E22').pack(pady=10)
            tk.Label(content, text="- Receive stock from warehouse\n- View inventory\n- Track transfers", 
                    bg='#FFF8F0', fg='#5D4E37').pack()
        else:
            tk.Label(content, text="\nWarehouse Functions:", 
                    font=("Arial", 10, "bold"), bg='#FFF8F0', fg='#E67E22').pack(pady=10)
            tk.Label(content, text="- Send stock to supermarket\n- Manage warehouse inventory\n- View all transfers", 
                    bg='#FFF8F0', fg='#5D4E37').pack()
        
        def logout():
            dashboard.destroy()
            root = tk.Tk()
            AuthWindow(root)
            root.mainloop()
        
        tk.Button(content, text="LOGOUT", command=logout,
                 bg='#E74C3C', fg='white', width=15, font=("Arial", 10, "bold"), relief='flat').pack(pady=20)
        
        dashboard.mainloop()

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()