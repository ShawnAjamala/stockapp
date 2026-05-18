import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    get_all_supermarket_products,
    record_sale,
    get_today_sales
)

# Page for recording sales and viewing today's sales history
class SupermarketSales(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user                        # logged‑in supermarket admin
        self.refresh_callback = refresh_callback  # function to refresh dashboard stats
        self.configure(bg='#F5F6FA')

        self.create_widgets()
        self.load_inventory()      # load current stock into the treeview
        self.load_today_sales()    # load today's sales into the treeview

    # Build the entire GUI layout
    def create_widgets(self):
        # Header with title
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="RECORD SALES", font=("Segoe UI", 18, "bold"),
                 bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        # ========== INVENTORY TABLE ==========
        inv_frame = tk.LabelFrame(self, text="CURRENT INVENTORY", font=("Segoe UI", 11, "bold"),
                                  bg='#FFFFFF', fg='#E67E22')
        inv_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Search bar for inventory
        search_frame = tk.Frame(inv_frame, bg='#FFFFFF')
        search_frame.pack(fill='x', pady=5, padx=10)
        tk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="SEARCH", command=self.search_inventory,
                  bg='#3498DB', fg='white').pack(side='left')
        tk.Button(search_frame, text="REFRESH", command=self.load_inventory,
                  bg='#95A5A6', fg='white').pack(side='left', padx=5)

        # Treeview container with scrollbar
        tree_container = tk.Frame(inv_frame, bg='#FFFFFF')
        tree_container.pack(fill='both', expand=True, padx=10, pady=5)

        scroll = ttk.Scrollbar(tree_container)
        scroll.pack(side='right', fill='y')

        columns = ('Name', 'Stock (KG)', 'Selling Price (Ksh/KG)')
        self.inv_tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                     yscrollcommand=scroll.set, height=10)
        scroll.config(command=self.inv_tree.yview)

        self.inv_tree.heading('Name', text='Product')
        self.inv_tree.heading('Stock (KG)', text='Stock (KG)')
        self.inv_tree.heading('Selling Price (Ksh/KG)', text='Selling Price (Ksh/KG)')

        self.inv_tree.column('Name', width=200)
        self.inv_tree.column('Stock (KG)', width=100)
        self.inv_tree.column('Selling Price (Ksh/KG)', width=170)
        self.inv_tree.pack(side='left', fill='both', expand=True)

        # ========== RECORD SALE FORM ==========
        sale_frame = tk.LabelFrame(self, text="RECORD SALE", font=("Segoe UI", 11, "bold"),
                                   bg='#FFFFFF', fg='#E67E22')
        sale_frame.pack(fill='x', padx=10, pady=5)

        sale_inner = tk.Frame(sale_frame, bg='#FFFFFF')
        sale_inner.pack(pady=15, padx=15)

        # Product selection
        tk.Label(sale_inner, text="Product:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.sale_product = ttk.Combobox(sale_inner, width=30, state='readonly')
        self.sale_product.grid(row=0, column=1, padx=10, pady=10)
        self.sale_product.bind('<<ComboboxSelected>>', self.on_sale_product_select)

        # Available stock display
        tk.Label(sale_inner, text="Available Stock:").grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.avail_stock_label = tk.Label(sale_inner, text="0 KG", fg='green')
        self.avail_stock_label.grid(row=0, column=3, padx=10, pady=10)

        # Selling price (pre‑filled from product's selling price)
        tk.Label(sale_inner, text="Selling Price (Ksh/KG):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.sale_price_entry = tk.Entry(sale_inner, width=15)
        self.sale_price_entry.grid(row=1, column=1, padx=10, pady=10)

        # Quantity sold
        tk.Label(sale_inner, text="Quantity Sold (KG):").grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.sale_qty_entry = tk.Entry(sale_inner, width=15)
        self.sale_qty_entry.grid(row=1, column=3, padx=10, pady=10)

        # Record sale button
        tk.Button(sale_inner, text="RECORD SALE", command=self.record_sale,
                  bg='#27AE60', fg='white', font=("Segoe UI", 11, "bold")).grid(row=2, column=0, columnspan=4, pady=15)

        # ========== TODAY'S SALES TABLE ==========
        today_frame = tk.LabelFrame(self, text="TODAY'S SALES", font=("Segoe UI", 11, "bold"),
                                    bg='#FFFFFF', fg='#E67E22')
        today_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Container with grid for scrollbars
        sales_container = tk.Frame(today_frame, bg='#FFFFFF')
        sales_container.pack(fill='both', expand=True, padx=10, pady=10)
        sales_container.columnconfigure(0, weight=1)
        sales_container.rowconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(sales_container, orient='vertical')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(sales_container, orient='horizontal')
        h_scroll.grid(row=1, column=0, sticky='ew')

        sales_columns = ('Product', 'Quantity (KG)', 'Selling Price (Ksh/KG)', 'Profit (Ksh)', 'Time')
        self.sales_tree = ttk.Treeview(sales_container, columns=sales_columns, show='headings',
                                       yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set, height=8)
        self.sales_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.config(command=self.sales_tree.yview)
        h_scroll.config(command=self.sales_tree.xview)

        for col in sales_columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=140)
        self.sales_tree.column('Product', width=180)

        # Summary bar (total KG sold & total profit)
        sum_frame = tk.Frame(today_frame, bg='#FEF9E7', relief='solid', bd=1)
        sum_frame.pack(fill='x', pady=5, padx=10)
        self.total_sales_label = tk.Label(sum_frame, text="Total KG sold today: 0", bg='#FEF9E7')
        self.total_sales_label.pack(side='left', padx=10, pady=5)
        self.total_profit_label = tk.Label(sum_frame, text="Total Profit: Ksh 0.00", bg='#FEF9E7', fg='green')
        self.total_profit_label.pack(side='right', padx=10, pady=5)

    # Load current inventory from database into the treeview
    def load_inventory(self):
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        products = get_all_supermarket_products()
        self.product_list = {p['name']: p for p in products}
        self.sale_product['values'] = list(self.product_list.keys())

        for p in products:
            self.inv_tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:.1f}",
                f"Ksh {p.get('selling_price', 0):.2f}"
            ))
        # Notify dashboard to refresh stats
        if self.refresh_callback:
            self.refresh_callback()

    # Filter inventory treeview by search keyword
    def search_inventory(self):
        kw = self.search_entry.get().strip().lower()
        self.inv_tree.delete(*self.inv_tree.get_children())
        for name, p in self.product_list.items():
            if kw in name.lower():
                self.inv_tree.insert('', 'end', values=(
                    name,
                    f"{p['quantity']:.1f}",
                    f"Ksh {p.get('selling_price', 0):.2f}"
                ))

    # When a product is selected for sale, show its available stock and pre‑filled selling price
    def on_sale_product_select(self, event):
        name = self.sale_product.get()
        if name in self.product_list:
            p = self.product_list[name]
            self.avail_stock_label.config(text=f"{p['quantity']:.2f} KG")
            selling = p.get('selling_price', 0)
            self.sale_price_entry.delete(0, tk.END)
            if selling > 0:
                self.sale_price_entry.insert(0, f"{selling:.2f}")

    # Record the sale, deduct stock, and update displays
    def record_sale(self):
        name = self.sale_product.get()
        if not name:
            messagebox.showerror("Error", "Select a product")
            return
        try:
            qty = float(self.sale_qty_entry.get())
            price = float(self.sale_price_entry.get())
        except:
            messagebox.showerror("Error", "Invalid quantity or price")
            return
        if qty <= 0 or price <= 0:
            messagebox.showerror("Error", "Values must be positive")
            return
        if name not in self.product_list:
            messagebox.showerror("Error", "Product not found")
            return
        avail = self.product_list[name]['quantity']
        if qty > avail:
            messagebox.showerror("Error", f"Only {avail:.2f} KG available")
            return
        ok, msg = record_sale(name, qty, price)
        if ok:
            messagebox.showinfo("Success", msg)
            self.load_inventory()          # refresh stock display
            self.load_today_sales()        # refresh today's sales table
            self.sale_product.set('')
            self.sale_qty_entry.delete(0, tk.END)
            self.sale_price_entry.delete(0, tk.END)
            if self.refresh_callback:
                self.refresh_callback()    # update dashboard stats
        else:
            messagebox.showerror("Error", msg)

    # Load today's sales from the database into the sales treeview
    def load_today_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        sales = get_today_sales()
        total_qty = 0
        total_profit = 0.0
        for s in sales:
            total_qty += s['quantity_sold']
            total_profit += s['profit']
            self.sales_tree.insert('', 'end', values=(
                s['product_name'],
                f"{s['quantity_sold']:.2f}",
                f"Ksh {s['selling_price']:.2f}",
                f"Ksh {s['profit']:.2f}",
                s['timestamp'].strftime('%H:%M')
            ))
        self.total_sales_label.config(text=f"Total KG sold today: {total_qty:.2f}")
        self.total_profit_label.config(text=f"Total Profit: Ksh {total_profit:.2f}")