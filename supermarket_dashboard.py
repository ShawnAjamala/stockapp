import tkinter as tk
from tkinter import ttk, messagebox
from supermarket_receive import SupermarketReceive
from supermarket_sales import SupermarketSales
from supermarket_profile import SupermarketProfile
from db import (
    get_all_supermarket_products, 
    get_today_profit, 
    get_unread_alerts,
    mark_alerts_as_read,
    get_all_alerts
)

class SupermarketDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"FreshStock Manager - Supermarket Dashboard")
        self.root.geometry("1100x650")
        self.root.configure(bg='#F5F6FA')
        
        self.current_frame = None
        self.center_window()
        self.create_widgets()
        self.show_dashboard()
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1100) // 2
        y = (self.root.winfo_screenheight() - 650) // 2
        self.root.geometry(f'1100x650+{x}+{y}')
    
    def create_widgets(self):
        # Top Navigation Bar
        nav_bar = tk.Frame(self.root, bg='#E67E22', height=65)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(nav_bar, bg='#E67E22')
        logo_frame.pack(side='left', padx=30, pady=12)
        tk.Label(logo_frame, text="FRESHSTOCK", font=("Segoe UI", 18, "bold"), bg='#E67E22', fg='white').pack(side='left')
        tk.Label(logo_frame, text="Supermarket", font=("Segoe UI", 10), bg='#E67E22', fg='#FAD7A1').pack(side='left', padx=(8,0))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Receive Stock", self.show_receive),
            ("Record Sales", self.show_sales),
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
        
        # Alert button
        self.update_alerts_count()
        self.alert_btn = tk.Button(nav_bar, text=self.alert_text, command=self.show_alerts,
                                   bg='#C0392B', fg='white', font=("Segoe UI", 9, "bold"),
                                   relief='flat', cursor='hand2', padx=15, pady=5)
        self.alert_btn.pack(side='right', padx=10)
        
        # Logout button
        logout_btn = tk.Button(nav_bar, text="LOGOUT", command=self.logout,
                              bg='#C0392B', fg='white', font=("Segoe UI", 10, "bold"),
                              relief='flat', cursor='hand2', padx=25, pady=8)
        logout_btn.pack(side='right', padx=10)
        
        # Main content area
        self.main_content = tk.Frame(self.root, bg='#F5F6FA')
        self.main_content.pack(fill="both", expand=True, padx=25, pady=20)
    
    def update_alerts_count(self):
        unread = get_unread_alerts()
        count = len(unread)
        self.alert_text = f"Alerts ({count})" if count > 0 else "No Alerts"
    
    def show_alerts(self):
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Notifications")
        alert_window.geometry("450x350")
        alert_window.configure(bg='#FFFFFF')
        alert_window.resizable(False, False)
        
        alert_window.update_idletasks()
        x = (alert_window.winfo_screenwidth() - 450) // 2
        y = (alert_window.winfo_screenheight() - 350) // 2
        alert_window.geometry(f'450x350+{x}+{y}')
        
        tk.Label(alert_window, text="NOTIFICATIONS", font=("Segoe UI", 14, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=15)
        
        alerts = get_all_alerts()
        if not alerts:
            tk.Label(alert_window, text="No notifications", font=("Segoe UI", 11), 
                    bg='#FFFFFF', fg='#7F8C8D').pack(pady=30)
        else:
            list_frame = tk.Frame(alert_window, bg='#FFFFFF')
            list_frame.pack(fill="both", expand=True, padx=15)
            
            for alert in alerts[-10:]:
                bg_color = '#FEF9E7' if not alert['read'] else '#FFFFFF'
                frame = tk.Frame(list_frame, bg=bg_color, relief='solid', bd=1)
                frame.pack(fill="x", pady=3)
                
                tk.Label(frame, text=alert['message'], font=("Segoe UI", 9), 
                        bg=bg_color, fg='#2C3E50').pack(anchor='w', padx=10, pady=5)
        
        def mark_read():
            mark_alerts_as_read()
            self.update_alerts_count()
            self.alert_btn.config(text=self.alert_text)
            alert_window.destroy()
        
        tk.Button(alert_window, text="MARK ALL AS READ", command=mark_read,
                 bg='#3498DB', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=5).pack(pady=15)
    
    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        self.current_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        self.current_frame.pack(fill="both", expand=True)
        
        # Hero Section
        hero_bg = tk.Frame(self.current_frame, bg='#E67E22', height=140)
        hero_bg.pack(fill="x")
        hero_bg.pack_propagate(False)
        
        hero_content = tk.Frame(hero_bg, bg='#E67E22')
        hero_content.pack(expand=True, pady=25)
        tk.Label(hero_content, text="WELCOME BACK", font=("Segoe UI", 11), 
                bg='#E67E22', fg='#FAD7A1').pack()
        tk.Label(hero_content, text=f"{self.user['fullname']}", font=("Segoe UI", 24, "bold"), 
                bg='#E67E22', fg='white').pack()
        
        # Get data
        products = get_all_supermarket_products()
        total_products = len(products)
        total_stock = sum(p['quantity'] for p in products)
        today_profit = get_today_profit()
        
        # 3 Stats Cards
        stats_frame = tk.Frame(self.current_frame, bg='#F5F6FA')
        stats_frame.pack(fill="x", pady=25)
        
        # Card 1 - Total Products
        card1 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=300, height=100)
        card1.pack(side='left', padx=15, fill='x', expand=True)
        card1.pack_propagate(False)
        tk.Label(card1, text="TOTAL PRODUCTS", font=("Segoe UI", 10), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(12, 5))
        tk.Label(card1, text=str(total_products), font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 2 - Total Stock
        card2 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=300, height=100)
        card2.pack(side='left', padx=15, fill='x', expand=True)
        card2.pack_propagate(False)
        tk.Label(card2, text="TOTAL STOCK", font=("Segoe UI", 10), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(12, 5))
        tk.Label(card2, text=f"{total_stock:,.0f} KG", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg='#E67E22').pack()
        
        # Card 3 - Today's Profit
        card3 = tk.Frame(stats_frame, bg='#FFFFFF', relief='raised', bd=1, width=300, height=100)
        card3.pack(side='left', padx=15, fill='x', expand=True)
        card3.pack_propagate(False)
        tk.Label(card3, text="TODAY'S PROFIT", font=("Segoe UI", 10), bg='#FFFFFF', fg='#7F8C8D').pack(pady=(12, 5))
        profit_color = '#27AE60' if today_profit >= 0 else '#E74C3C'
        tk.Label(card3, text=f"${today_profit:,.2f}", font=("Segoe UI", 28, "bold"), bg='#FFFFFF', fg=profit_color).pack()
        
        # Refresh button
        tk.Button(self.current_frame, text="REFRESH", command=self.refresh_dashboard,
                 bg='#3498DB', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=20, pady=8).pack(pady=20)
    
    def refresh_dashboard(self):
        self.show_dashboard()
        self.update_alerts_count()
        self.alert_btn.config(text=self.alert_text)
    
    def show_receive(self):
        self.clear_content()
        self.current_frame = SupermarketReceive(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_sales(self):
        self.clear_content()
        self.current_frame = SupermarketSales(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_profile(self):
        self.clear_content()
        self.current_frame = SupermarketProfile(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from auth import AuthWindow
            root = tk.Tk()
            AuthWindow(root)
            root.mainloop()