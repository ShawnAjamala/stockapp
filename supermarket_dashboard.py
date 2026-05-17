import tkinter as tk
from tkinter import ttk, messagebox
from supermarket_receive import SupermarketReceive
from supermarket_sales import SupermarketSales
from supermarket_profile import SupermarketProfile
from supermarket_transfers import SupermarketTransfers
from db import get_all_supermarket_products, get_today_profit
from datetime import datetime

class SupermarketDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("FreshStock Manager - Supermarket Dashboard")
        self.root.geometry("1100x650")
        self.root.configure(bg='#F5F6FA')
        self.current_frame = None

        # Stat label references
        self.card1_val = None   # Total Products
        self.card2_val = None   # Total Stock
        self.card3_val = None   # Today's Profit

        self.center_window()
        self.create_widgets()
        self.show_dashboard()

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1100) // 2
        y = (self.root.winfo_screenheight() - 650) // 2
        self.root.geometry(f'1100x650+{x}+{y}')

    def _widget_alive(self, widget):
        try:
            return widget is not None and widget.winfo_exists()
        except:
            return False

    def create_widgets(self):
        # Navigation bar
        nav_bar = tk.Frame(self.root, bg='#E67E22', height=65)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)

        logo_frame = tk.Frame(nav_bar, bg='#E67E22')
        logo_frame.pack(side='left', padx=30, pady=12)
        tk.Label(logo_frame, text="FRESHSTOCK", font=("Segoe UI", 18, "bold"),
                 bg='#E67E22', fg='white').pack(side='left')
        tk.Label(logo_frame, text="Supermarket", font=("Segoe UI", 10),
                 bg='#E67E22', fg='#FAD7A1').pack(side='left', padx=(8, 0))

        nav_buttons = [
            ("Dashboard",   self.show_dashboard),
            ("Receive Stock", self.show_receive),
            ("Record Sales",  self.show_sales),
            ("Transfers",     self.show_transfers),   # ← NEW
            ("Profile",       self.show_profile)
        ]
        nav_frame = tk.Frame(nav_bar, bg='#E67E22')
        nav_frame.pack(side='left', padx=30)

        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                            bg='#E67E22', fg='white', font=("Segoe UI", 10),
                            relief='flat', cursor='hand2', padx=15, pady=8)
            btn.pack(side='left', padx=3)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#D35400'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#E67E22'))

        tk.Button(nav_bar, text="LOGOUT", command=self.logout,
                  bg='#C0392B', fg='white', font=("Segoe UI", 10, "bold"),
                  relief='flat', cursor='hand2', padx=25, pady=8).pack(side='right', padx=30)

        self.main_content = tk.Frame(self.root, bg='#F5F6FA')
        self.main_content.pack(fill="both", expand=True, padx=25, pady=20)

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
        self.card1_val = self.card2_val = self.card3_val = None

    def show_dashboard(self):
        self.clear_content()

        self.current_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        self.current_frame.pack(fill="both", expand=True)

        # Hero section
        hero_bg = tk.Frame(self.current_frame, bg='#E67E22', height=140)
        hero_bg.pack(fill="x")
        hero_bg.pack_propagate(False)
        hero_content = tk.Frame(hero_bg, bg='#E67E22')
        hero_content.pack(expand=True, pady=25)
        tk.Label(hero_content, text="WELCOME BACK", font=("Segoe UI", 11),
                 bg='#E67E22', fg='#FAD7A1').pack()
        tk.Label(hero_content, text=self.user['fullname'], font=("Segoe UI", 24, "bold"),
                 bg='#E67E22', fg='white').pack()

        # Fetch data
        products = get_all_supermarket_products()
        total_products = len(products)
        total_stock = sum(p['quantity'] for p in products)
        today_profit = get_today_profit()

        # Stats cards
        stats_frame = tk.Frame(self.current_frame, bg='#F5F6FA')
        stats_frame.pack(fill="x", pady=25)

        def make_card(parent, title, value_text, value_color, attr_name):
            card = tk.Frame(parent, bg='#FFFFFF', relief='raised', bd=1,
                            width=300, height=100)
            card.pack(side='left', padx=15, fill='x', expand=True)
            card.pack_propagate(False)
            tk.Label(card, text=title, font=("Segoe UI", 10),
                     bg='#FFFFFF', fg='#7F8C8D').pack(pady=(12, 5))
            lbl = tk.Label(card, text=value_text, font=("Segoe UI", 28, "bold"),
                           bg='#FFFFFF', fg=value_color)
            lbl.pack()
            setattr(self, attr_name, lbl)

        make_card(stats_frame, "TOTAL PRODUCTS", str(total_products), '#E67E22', 'card1_val')
        make_card(stats_frame, "TOTAL STOCK", f"{total_stock:,.0f} KG", '#E67E22', 'card2_val')
        profit_color = '#27AE60' if today_profit >= 0 else '#E74C3C'
        make_card(stats_frame, "TODAY'S PROFIT", f"${today_profit:,.2f}", profit_color, 'card3_val')

        # Quick-nav buttons
        quick_frame = tk.Frame(self.current_frame, bg='#F5F6FA')
        quick_frame.pack(pady=10)

        quick_actions = [
            ("Receive Stock",   self.show_receive,   '#27AE60'),
            ("Record Sales",    self.show_sales,     '#3498DB'),
            ("View Transfers",  self.show_transfers, '#8E44AD'),
        ]
        for label, cmd, color in quick_actions:
            tk.Button(quick_frame, text=label, command=cmd,
                      bg=color, fg='white', font=("Segoe UI", 10, "bold"),
                      relief='flat', cursor='hand2', padx=20, pady=8).pack(side='left', padx=10)

        tk.Button(self.current_frame, text="REFRESH STATS", command=self.refresh_dashboard,
                  bg='#95A5A6', fg='white', font=("Segoe UI", 9),
                  relief='flat', cursor='hand2', padx=15, pady=6).pack(pady=10)

    def refresh_dashboard(self):
        if not self._widget_alive(self.card1_val):
            return

        products = get_all_supermarket_products()
        total_products = len(products)
        total_stock = sum(p['quantity'] for p in products)
        today_profit = get_today_profit()

        if self._widget_alive(self.card1_val):
            self.card1_val.config(text=str(total_products))
        if self._widget_alive(self.card2_val):
            self.card2_val.config(text=f"{total_stock:,.0f} KG")
        if self._widget_alive(self.card3_val):
            profit_color = '#27AE60' if today_profit >= 0 else '#E74C3C'
            self.card3_val.config(text=f"${today_profit:,.2f}", fg=profit_color)

    def show_receive(self):
        self.clear_content()
        self.current_frame = SupermarketReceive(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)

    def show_sales(self):
        self.clear_content()
        self.current_frame = SupermarketSales(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)

    def show_transfers(self):                          # ← NEW
        self.clear_content()
        self.current_frame = SupermarketTransfers(self.main_content, self.user, self.refresh_dashboard)
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