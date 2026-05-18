import tkinter as tk
from tkinter import ttk, messagebox
from warehouse_stock import WarehouseStock
from warehouse_send import WarehouseSend
from warehouse_transfers import WarehouseTransfers
from warehouse_profile import WarehouseProfile
from db import (
    get_all_warehouse_products,
    get_all_movements,
    get_pending_requests_for_warehouse,
)
from datetime import datetime

# Main dashboard for warehouse admin – shows stats, activity, and navigation
class WarehouseDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("FreshStock Manager - Warehouse Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg='#F5F6FA')
        self.current_frame = None

        # Dashboard stat label references – set to None when another page is active
        self.pending_label      = None   # label for pending requests count
        self.sent_label         = None   # label for stock sent today (KG)
        self.inv_value_label    = None   # label for total inventory value ($)
        self.totalprod_label    = None   # label for total number of products
        self.activity_text      = None   # text widget for recent activity

        self.center_window()
        self.create_widgets()
        self.show_dashboard()

    # Center the dashboard window on the screen
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 1200) // 2
        y = (self.root.winfo_screenheight() - 700)  // 2
        self.root.geometry(f'1200x700+{x}+{y}')

    # Check if a tkinter widget still exists (not destroyed) – used to avoid update errors
    def _widget_alive(self, widget):
        try:
            return widget is not None and widget.winfo_exists()
        except Exception:
            return False

    # Build the top navigation bar and the main content area
    def create_widgets(self):
        # ── Navigation bar (orange) ────────────────────────────────────────────
        nav_bar = tk.Frame(self.root, bg='#E67E22', height=65)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)

        # Logo and title
        logo_frame = tk.Frame(nav_bar, bg='#E67E22')
        logo_frame.pack(side='left', padx=30, pady=12)
        tk.Label(logo_frame, text="FRESHSTOCK", font=("Segoe UI", 18, "bold"),
                 bg='#E67E22', fg='white').pack(side='left')
        tk.Label(logo_frame, text="Warehouse", font=("Segoe UI", 10),
                 bg='#E67E22', fg='#FAD7A1').pack(side='left', padx=(8, 0))

        # Navigation buttons (Dashboard, Warehouse Stock, Send Stock, Transfers, Profile)
        nav_buttons = [
            ("Dashboard",       self.show_dashboard),
            ("Warehouse Stock", self.show_stock),
            ("Send Stock",      self.show_send),
            ("Transfers",       self.show_transfers),
            ("Profile",         self.show_profile),
        ]
        nav_frame = tk.Frame(nav_bar, bg='#E67E22')
        nav_frame.pack(side='left', padx=50)

        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                            bg='#E67E22', fg='white', font=("Segoe UI", 10),
                            relief='flat', cursor='hand2', padx=20, pady=8)
            btn.pack(side='left', padx=5)
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#D35400'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#E67E22'))

        # Logout button (always visible on the right)
        tk.Button(nav_bar, text="LOGOUT", command=self.logout,
                  bg='#C0392B', fg='white', font=("Segoe UI", 10, "bold"),
                  relief='flat', cursor='hand2', padx=25, pady=8
                  ).pack(side='right', padx=30)

        # Main content area where different pages are displayed
        self.main_content = tk.Frame(self.root, bg='#F5F6FA')
        self.main_content.pack(fill="both", expand=True, padx=25, pady=20)

    # ── Page switching ────────────────────────────────────────────────
    def clear_content(self):
        """Destroy the current page and reset all dashboard widget references."""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

        # Reset stat label references; they will be recreated when the dashboard is shown
        self.pending_label   = None
        self.sent_label      = None
        self.inv_value_label = None
        self.totalprod_label = None
        self.activity_text   = None

    # Display the main dashboard view (stats cards, recent activity)
    def show_dashboard(self):
        self.clear_content()

        self.current_frame = tk.Frame(self.main_content, bg='#F5F6FA')
        self.current_frame.pack(fill="both", expand=True)

        # ── Hero section (orange banner with welcome message) ──────────────────
        hero_bg = tk.Frame(self.current_frame, bg='#E67E22', height=140)
        hero_bg.pack(fill="x")
        hero_bg.pack_propagate(False)
        hero_content = tk.Frame(hero_bg, bg='#E67E22')
        hero_content.pack(expand=True, pady=25)
        tk.Label(hero_content, text="WELCOME BACK", font=("Segoe UI", 11),
                 bg='#E67E22', fg='#FAD7A1').pack()
        tk.Label(hero_content, text=self.user['fullname'], font=("Segoe UI", 24, "bold"),
                 bg='#E67E22', fg='white').pack()
        tk.Label(hero_content, text="Warehouse Administrator Dashboard",
                 font=("Segoe UI", 11), bg='#E67E22', fg='#FAD7A1').pack()

        # ── Fetch statistics from the database ─────────────────────────────────
        pending      = len(get_pending_requests_for_warehouse(self.user['email']))
        products     = get_all_warehouse_products()
        total_prods  = len(products)
        inv_value    = sum(p['quantity'] * p['price'] for p in products)

        today        = datetime.now().strftime("%Y-%m-%d")
        movements    = get_all_movements()
        sent_today   = sum(
            m['quantity'] for m in movements
            if m.get('movement_type') == 'OUT' and m.get('date') == today
        )

        # ── Create the four statistic cards (horizontal row) ───────────────────
        stats_frame = tk.Frame(self.current_frame, bg='#F5F6FA')
        stats_frame.pack(fill="x", pady=20)

        # Helper to build a card and store the value label reference
        def make_card(parent, title, value_text, value_color, label_attr):
            card = tk.Frame(parent, bg='#FFFFFF', relief='raised', bd=1,
                            width=270, height=110)
            card.pack(side='left', padx=10, fill='x', expand=True)
            card.pack_propagate(False)
            tk.Label(card, text=title, font=("Segoe UI", 11),
                     bg='#FFFFFF', fg='#7F8C8D').pack(pady=(12, 5))
            lbl = tk.Label(card, text=value_text,
                           font=("Segoe UI", 28, "bold"),
                           bg='#FFFFFF', fg=value_color)
            lbl.pack()
            setattr(self, label_attr, lbl)

        make_card(stats_frame, "PENDING REQUESTS",  str(pending),
                  '#E67E22', 'pending_label')
        make_card(stats_frame, "STOCK SENT TODAY",  f"{sent_today:.1f} KG",
                  '#E67E22', 'sent_label')
        make_card(stats_frame, "INVENTORY VALUE",   f"Ksh{inv_value:,.2f}",
                  '#27AE60', 'inv_value_label')
        make_card(stats_frame, "TOTAL PRODUCTS",    str(total_prods),
                  '#E67E22', 'totalprod_label')

        # ── Recent activity feed (last 10 stock movements) ─────────────────────
        activity_frame = tk.Frame(self.current_frame, bg='#FFFFFF', relief='flat', bd=1)
        activity_frame.pack(fill="both", expand=True, pady=20)

        tk.Label(activity_frame, text="RECENT ACTIVITY", font=("Segoe UI", 12, "bold"),
                 bg='#FFFFFF', fg='#2C3E50').pack(anchor='w', padx=20, pady=15)

        self.activity_text = tk.Text(activity_frame, height=10, bg='#F8F9FA',
                                     fg='#5D4E37', font=("Segoe UI", 10), relief='flat')
        self.activity_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.load_recent_activity()

        # Manual refresh button (also auto‑refreshed via callbacks)
        tk.Button(self.current_frame, text="REFRESH DASHBOARD",
                  command=self.refresh_dashboard,
                  bg='#3498DB', fg='white', font=("Segoe UI", 10, "bold"),
                  relief='flat', cursor='hand2', padx=20, pady=8).pack(pady=10)

    # Load the most recent stock movements into the activity text widget
    def load_recent_activity(self):
        if not self._widget_alive(self.activity_text):
            return

        movements = get_all_movements()
        self.activity_text.configure(state='normal')
        self.activity_text.delete(1.0, tk.END)
        if movements:
            for m in movements[:10]:
                ts = m['timestamp'].strftime('%Y-%m-%d %H:%M')
                line = (f"[{ts}] {m['movement_type']}: {m['quantity']:.2f} KG "
                        f"of {m['product_name']} – {m.get('notes', '')}\n")
                self.activity_text.insert(tk.END, line)
        else:
            self.activity_text.insert(tk.END, "No recent activity")
        self.activity_text.configure(state='disabled')

    # Update the stat cards and activity feed without rebuilding the whole dashboard
    def refresh_dashboard(self):
        # Safety: only update if the dashboard is currently visible
        if not self._widget_alive(self.pending_label):
            return

        products   = get_all_warehouse_products()
        pending    = len(get_pending_requests_for_warehouse(self.user['email']))
        total_prods = len(products)
        inv_value  = sum(p['quantity'] * p['price'] for p in products)

        today      = datetime.now().strftime("%Y-%m-%d")
        movements  = get_all_movements()
        sent_today = sum(
            m['quantity'] for m in movements
            if m.get('movement_type') == 'OUT' and m.get('date') == today
        )

        # Update each label only if it still exists
        if self._widget_alive(self.pending_label):
            self.pending_label.config(text=str(pending))
        if self._widget_alive(self.sent_label):
            self.sent_label.config(text=f"{sent_today:.1f} KG")
        if self._widget_alive(self.inv_value_label):
            self.inv_value_label.config(text=f"${inv_value:,.2f}")
        if self._widget_alive(self.totalprod_label):
            self.totalprod_label.config(text=str(total_prods))

        self.load_recent_activity()

    # ── Page navigation methods ──────────────────────────────────────────────────
    def show_stock(self):
        # Switch to the Warehouse Stock management page
        self.clear_content()
        self.current_frame = WarehouseStock(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)

    def show_send(self):
        # Switch to the Send Stock page (requests & direct send)
        self.clear_content()
        self.current_frame = WarehouseSend(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)

    def show_transfers(self):
        # Switch to the Transfers page (IN/OUT movements history)
        self.clear_content()
        self.current_frame = WarehouseTransfers(self.main_content, self.user, self.refresh_dashboard)
        self.current_frame.pack(fill="both", expand=True)

    def show_profile(self):
        # Switch to the Profile page
        self.clear_content()
        self.current_frame = WarehouseProfile(self.main_content, self.user)
        self.current_frame.pack(fill="both", expand=True)

    def logout(self):
        # Confirm and return to the login screen
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from auth import AuthWindow
            root = tk.Tk()
            AuthWindow(root)
            root.mainloop()