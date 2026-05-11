"""
AUTHENTICATION GUI MODULE - Login and Registration interface
Simplified: Only Email, Password, and Full Name for registration
"""
import tkinter as tk
from tkinter import ttk, messagebox
from db import verify_user, register_user, get_user_info

class AuthWindow:
    """Main authentication window with login and register tabs"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket Storage System - Login")
        self.root.geometry("500x600")  # FIXED: was "500"600" now "500x600"
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Center window on screen
        self.center_window()
        
        # Create UI
        self.create_widgets()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = 500
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(header_frame, text="🏪 SUPERMARKET STORAGE SYSTEM", 
                        font=("Arial", 16, "bold"), bg='#2c3e50', fg='white')
        title.pack(pady=(30, 5))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Inventory Management System", 
                           font=("Arial", 10), bg='#2c3e50', fg='#ecf0f1')
        subtitle.pack()
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Login Tab
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="🔐 LOGIN")
        self.create_login_tab()
        
        # Register Tab
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="📝 REGISTER")
        self.create_register_tab()
    
    def create_login_tab(self):
        """Create login tab content"""
        
        # Main container
        container = tk.Frame(self.login_frame, bg='white')
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Welcome message
        welcome = tk.Label(container, text="Welcome Back!", 
                          font=("Arial", 14, "bold"), bg='white', fg='#2c3e50')
        welcome.pack(pady=(0, 30))
        
        # Email field
        tk.Label(container, text="Email Address:", font=("Arial", 11), 
                bg='white', anchor='w').pack(fill="x", pady=(0, 5))
        self.login_email = tk.Entry(container, width=30, font=("Arial", 11),
                                    bg='white', relief='solid', bd=1)
        self.login_email.pack(fill="x", pady=(0, 20))
        self.login_email.bind('<Return>', lambda e: self.login())
        
        # Password field
        tk.Label(container, text="Password:", font=("Arial", 11), 
                bg='white', anchor='w').pack(fill="x", pady=(0, 5))
        self.login_password = tk.Entry(container, show="•", width=30, font=("Arial", 11),
                                       bg='white', relief='solid', bd=1)
        self.login_password.pack(fill="x", pady=(0, 30))
        self.login_password.bind('<Return>', lambda e: self.login())
        
        # Login Button
        login_btn = tk.Button(container, text="LOGIN", command=self.login,
                              bg='#3498db', fg='white', font=("Arial", 12, "bold"),
                              relief='raised', bd=2, cursor='hand2')
        login_btn.pack(fill="x", pady=(0, 20))
        
        # Demo credentials box
        info_frame = tk.Frame(container, bg='#ecf0f1', relief='solid', bd=1)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ Demo Credentials", 
                font=("Arial", 10, "bold"), bg='#ecf0f1', fg='#2c3e50').pack(pady=(10, 5))
        tk.Label(info_frame, text="Email: admin@supermarket.com\nPassword: admin123", 
                font=("Arial", 9), bg='#ecf0f1', fg='#7f8c8d', justify='left').pack(pady=(0, 10))
    
    def create_register_tab(self):
        """Create register tab - Only Full Name, Email, Password (no confirm)"""
        
        # Main container
        container = tk.Frame(self.register_frame, bg='white')
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title = tk.Label(container, text="Create New Account", 
                        font=("Arial", 14, "bold"), bg='white', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Full Name field
        tk.Label(container, text="Full Name:", font=("Arial", 11), 
                bg='white', anchor='w').pack(fill="x", pady=(0, 5))
        self.register_fullname = tk.Entry(container, width=30, font=("Arial", 11),
                                          bg='white', relief='solid', bd=1)
        self.register_fullname.pack(fill="x", pady=(0, 15))
        
        # Email field
        tk.Label(container, text="Email Address:", font=("Arial", 11), 
                bg='white', anchor='w').pack(fill="x", pady=(0, 5))
        self.register_email = tk.Entry(container, width=30, font=("Arial", 11),
                                       bg='white', relief='solid', bd=1)
        self.register_email.pack(fill="x", pady=(0, 15))
        
        # Password field (only once, no confirm)
        tk.Label(container, text="Password:", font=("Arial", 11), 
                bg='white', anchor='w').pack(fill="x", pady=(0, 5))
        self.register_password = tk.Entry(container, show="•", width=30, font=("Arial", 11),
                                          bg='white', relief='solid', bd=1)
        self.register_password.pack(fill="x", pady=(0, 25))
        
        # REGISTER Button
        register_btn = tk.Button(container, text="REGISTER", command=self.register,
                                 bg='#2ecc71', fg='white', font=("Arial", 12, "bold"),
                                 relief='raised', bd=2, cursor='hand2')
        register_btn.pack(fill="x", pady=(0, 15))
        
        # Password requirements box
        req_frame = tk.Frame(container, bg='#fff3e0', relief='solid', bd=1)
        req_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(req_frame, text="📋 Password Requirements", 
                font=("Arial", 9, "bold"), bg='#fff3e0', fg='#e67e22').pack(pady=(8, 3))
        tk.Label(req_frame, text="• Minimum 4 characters\n• Can include letters and numbers", 
                font=("Arial", 8), bg='#fff3e0', fg='#7f8c8d', justify='left').pack(pady=(0, 8))
        
        # Note about no confirm password
        note_label = tk.Label(container, text="💡 Tip: Make sure you remember your password!", 
                             font=("Arial", 8), bg='white', fg='#95a5a6')
        note_label.pack(pady=(5, 0))
    
    def login(self):
        """Handle login using email"""
        email = self.login_email.get().strip()
        password = self.login_password.get()
        
        if not email:
            messagebox.showerror("Error", "❌ Please enter email address")
            return
        
        if not password:
            messagebox.showerror("Error", "❌ Please enter password")
            return
        
        if verify_user(email, password):
            user_info = get_user_info(email)
            name = user_info.get('fullname', email) if user_info else email
            messagebox.showinfo("Success", f"✅ Welcome {name}!\n\nLogin successful!")
            self.root.destroy()
            self.open_main_app(email)
        else:
            messagebox.showerror("Error", "❌ Invalid email or password!\n\nDemo: admin@supermarket.com / admin123")
    
    def register(self):
        """Handle registration - only email, password, fullname"""
        fullname = self.register_fullname.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get()
        
        # Validation
        if not fullname:
            messagebox.showerror("Error", "❌ Please enter your full name")
            return
        
        if not email:
            messagebox.showerror("Error", "❌ Please enter email address")
            return
        
        # Basic email validation
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "❌ Please enter a valid email address\n(e.g., name@example.com)")
            return
        
        if not password:
            messagebox.showerror("Error", "❌ Please enter a password")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "❌ Password must be at least 4 characters")
            return
        
        # Register user
        success, message = register_user(email, password, fullname)
        
        if success:
            messagebox.showinfo("Success", f"✅ {message}\n\nYou can now login with your email and password!")
            # Clear fields
            self.register_fullname.delete(0, tk.END)
            self.register_email.delete(0, tk.END)
            self.register_password.delete(0, tk.END)
            # Switch to login tab
            self.notebook.select(0)
            # Pre-fill email field in login tab
            self.login_email.delete(0, tk.END)
            self.login_email.insert(0, email)
        else:
            messagebox.showerror("Error", f"❌ {message}")
    
    def open_main_app(self, email):
        """Open main application (placeholder)"""
        user_info = get_user_info(email)
        
        # Create a simple welcome window
        welcome_root = tk.Tk()
        welcome_root.title("Supermarket Storage System - Dashboard")
        welcome_root.geometry("550x450")
        welcome_root.configure(bg='#f0f0f0')
        
        # Center window
        welcome_root.update_idletasks()
        x = (welcome_root.winfo_screenwidth() // 2) - (275)
        y = (welcome_root.winfo_screenheight() // 2) - (225)
        welcome_root.geometry(f'550x450+{x}+{y}')
        
        # Header
        header = tk.Frame(welcome_root, bg='#2c3e50', height=100)
        header.pack(fill="x")
        
        tk.Label(header, text="🏪 SUPERMARKET STORAGE SYSTEM", 
                font=("Arial", 16, "bold"), bg='#2c3e50', fg='white').pack(pady=30)
        
        # Content
        content = tk.Frame(welcome_root, bg='#f0f0f0')
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Welcome message with user info
        tk.Label(content, text=f"Welcome, {user_info.get('fullname', email)}!", 
                font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)
        
        tk.Label(content, text=f"Email: {user_info['email']}", 
                font=("Arial", 11), bg='#f0f0f0', fg='#7f8c8d').pack(pady=(0, 30))
        
        tk.Label(content, text="✓ Authentication Successful!\n\nMain application coming soon...", 
                font=("Arial", 10), bg='#f0f0f0', fg='#27ae60', justify='center').pack(pady=20)
        
        def logout():
            welcome_root.destroy()
            # Restart auth window
            root = tk.Tk()
            app = AuthWindow(root)
            root.mainloop()
        
        tk.Button(content, text="LOGOUT", command=logout,
                 bg='#e74c3c', fg='white', font=("Arial", 11, "bold"),
                 width=15, cursor='hand2').pack(pady=20)
        
        welcome_root.mainloop()

# ==================== RUN THE APP ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()