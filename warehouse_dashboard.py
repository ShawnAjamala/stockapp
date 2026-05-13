import tkinter as tk
from tkinter import ttk, messagebox
from warehouse_stock import WarehouseStock
from warehouse_send import WarehouseSend
from warehouse_transfers import WarehouseTransfers
from warehouse_profile import WarehouseProfile

class WarehouseDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"FreshStock Manager - Warehouse Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg='#F5F6FA')
        
        self.current_frame = None
        self.center_window()
        self.create_widgets()
        
        # Show dashboard by default
        self.show_dashboard()
    
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
        tk.Label(logo_frame, text="Warehouse", font=("Segoe UI", 10), bg='#E67E22', fg='#FAD7A1').pack(side='left', padx=(8,0))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Warehouse Stock", self.show_stock),
            ("Send Stock", self.show_send),
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
    
    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Create dashboard frame
        self.current_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        self.current_frame.pack(fill="both", expand=True)
        
        # Hero Section
        hero_frame = tk.Frame(self.current_frame, bg='#FFFFFF', relief='flat')
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
        tk.Label(hero_content, text="Warehouse Administrator Dashboard", font=("Segoe UI", 11), 
                bg='#E67E22', fg='#FAD7A1').pack()
        
        # Stats Cards
        stats_frame = tk.Frame(self.current_frame, bg='#F5F6FA')
        stats_frame.pack(fill="x", pady=20)
        
        # Card 1
        card1 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card1.pack(side='left', padx=10, fill='x', expand=True)
        card1.pack_propagate(False)
        tk.Label(card1, text="WAREHOUSE STOCK", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card1, text="0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 2
        card2 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card2.pack(side='left', padx=10, fill='x', expand=True)
        card2.pack_propagate(False)
        tk.Label(card2, text="STOCK SENT", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card2, text="0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 3
        card3 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=320, height=110)
        card3.pack(side='left', padx=10, fill='x', expand=True)
        card3.pack_propagate(False)
        tk.Label(card3, text="INVENTORY VALUE", font=("Segoe UI", 11), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(15, 5))
        tk.Label(card3, text="$0", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Recent Activity
        activity_frame = tk.Frame(self.current_frame, bg='#FFFFFF', relief='flat', bd=1)
        activity_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(activity_frame, text="RECENT ACTIVITY", font=("Segoe UI", 12, "bold"), 
                bg='#FFFFFF', fg='#2C3E50').pack(anchor='w', padx=20, pady=15)
        
        activity_text = tk.Text(activity_frame, height=8, bg='#F8F9FA', fg='#5D4E37', 
                               font=("Segoe UI", 10), relief='flat')
        activity_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        activity_text.insert('1.0', "No recent activity yet\nUse the navigation menu to manage warehouse inventory")
        activity_text.configure(state='disabled')
    
    def show_stock(self):
        self.clear_content()
        self.current_frame = WarehouseStock(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_send(self):
        self.clear_content()
        self.current_frame = WarehouseSend(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_transfers(self):
        self.clear_content()
        self.current_frame = WarehouseTransfers(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_profile(self):
        self.clear_content()
        self.current_frame = WarehouseProfile(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from auth import AuthWindow
            root = tk.Tk()
            AuthWindow(root)
            root.mainloop()