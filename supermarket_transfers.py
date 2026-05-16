import tkinter as tk
from tkinter import ttk, messagebox
from db import get_all_transfers, get_all_sales

class SupermarketTransfers(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user
        self.refresh_callback = refresh_callback
        self.configure(bg='#F5F6FA')

        self.create_widgets()
        self.load_transfers()
        self.load_sales()

    def create_widgets(self):
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="TRANSFERS & SALES HISTORY",
                 font=("Segoe UI", 18, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # ----- Tab 1: Stock Received -----
        trans_tab = ttk.Frame(notebook)
        notebook.add(trans_tab, text="📥 STOCK RECEIVED")

        trans_container = tk.Frame(trans_tab, bg='#FFFFFF')
        trans_container.pack(fill='both', expand=True, padx=10, pady=10)
        trans_container.columnconfigure(0, weight=1)
        trans_container.rowconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(trans_container, orient='vertical')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(trans_container, orient='horizontal')
        h_scroll.grid(row=1, column=0, sticky='ew')

        columns = ('Product', 'Quantity (KG)', 'From Warehouse', 'Date')
        self.trans_tree = ttk.Treeview(trans_container, columns=columns, show='headings',
                                       yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.trans_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.config(command=self.trans_tree.yview)
        h_scroll.config(command=self.trans_tree.xview)

        for col in columns:
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=150)

        tk.Button(trans_tab, text="REFRESH TRANSFERS", command=self.load_transfers,
                  bg='#3498DB', fg='white').pack(pady=5)

        # ----- Tab 2: Sales History -----
        sales_tab = ttk.Frame(notebook)
        notebook.add(sales_tab, text="💰 SALES HISTORY")

        sales_container = tk.Frame(sales_tab, bg='#FFFFFF')
        sales_container.pack(fill='both', expand=True, padx=10, pady=10)
        sales_container.columnconfigure(0, weight=1)
        sales_container.rowconfigure(0, weight=1)

        v_scroll2 = ttk.Scrollbar(sales_container, orient='vertical')
        v_scroll2.grid(row=0, column=1, sticky='ns')
        h_scroll2 = ttk.Scrollbar(sales_container, orient='horizontal')
        h_scroll2.grid(row=1, column=0, sticky='ew')

        sales_columns = ('Product', 'Quantity (KG)', 'Selling Price ($/KG)', 'Profit ($)', 'Date', 'Time')
        self.sales_tree = ttk.Treeview(sales_container, columns=sales_columns, show='headings',
                                       yscrollcommand=v_scroll2.set, xscrollcommand=h_scroll2.set)
        self.sales_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll2.config(command=self.sales_tree.yview)
        h_scroll2.config(command=self.sales_tree.xview)

        for col in sales_columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120)
        self.sales_tree.column('Product', width=180)

        tk.Button(sales_tab, text="REFRESH SALES", command=self.load_sales,
                  bg='#2ECC71', fg='white').pack(pady=5)

    def load_transfers(self):
        for row in self.trans_tree.get_children():
            self.trans_tree.delete(row)

        all_trans = get_all_transfers()
        for t in all_trans:
            # Show only transfers where this supermarket is the receiver
            if t.get('to_email') == self.user['email']:
                self.trans_tree.insert('', 'end', values=(
                    t['product_name'],
                    f"{t['quantity']:.2f}",
                    t.get('from_email', 'Unknown'),
                    t['timestamp'].strftime('%Y-%m-%d %H:%M')
                ))
        if self.refresh_callback:
            self.refresh_callback()

    def load_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales = get_all_sales()
        for sale in sales:
            dt = sale['timestamp']
            self.sales_tree.insert('', 'end', values=(
                sale['product_name'],
                f"{sale['quantity_sold']:.2f}",
                f"${sale['selling_price']:.2f}",
                f"${sale['profit']:.2f}",
                dt.strftime('%Y-%m-%d'),
                dt.strftime('%H:%M:%S')
            ))
        if self.refresh_callback:
            self.refresh_callback()