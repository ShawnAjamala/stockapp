import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bson import ObjectId
from pymongo import MongoClient
import csv

# Connect directly to MongoDB (separate from the main db.py module)
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")
db = client.supermarket_storage

class SupermarketTransfers(tk.Frame):
    # Displays incoming stock transfers (from warehouse) and outgoing sales records
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user                        # logged‑in supermarket admin
        self.refresh_callback = refresh_callback  # callback to refresh dashboard stats
        self.configure(bg='#F5F6FA')
        self._in_ids = []   # store tuples (treeview_id, db_id) for incoming records
        self._out_ids = []  # same for outgoing (sales) records

        self.create_widgets()
        self.load_incoming()
        self.load_outgoing()

    # Build the two‑tab interface
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SUPERMARKET TRANSFERS",
                 font=("Segoe UI", 18, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        # Notebook (tabbed pane)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Tab 1 – Incoming (stock received from warehouse)
        self.incoming_tab = tk.Frame(self.notebook, bg='#F5F6FA')
        self.notebook.add(self.incoming_tab, text='  INCOMING  (From Warehouse)  ')

        # Tab 2 – Outgoing (sales recorded by supermarket)
        self.outgoing_tab = tk.Frame(self.notebook, bg='#F5F6FA')
        self.notebook.add(self.outgoing_tab, text='  OUTGOING  (Sales)  ')

        # Build the individual tabs
        self._build_incoming_tab()
        self._build_outgoing_tab()

    # ── INCOMING TAB ──────────────────────────────
    def _build_incoming_tab(self):
        tab = self.incoming_tab

        # Control bar with action buttons
        ctrl = tk.Frame(tab, bg='#F5F6FA')
        ctrl.pack(fill='x', padx=10, pady=8)
        tk.Button(ctrl, text="REFRESH", command=self.load_incoming,
                  bg='#3498DB', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)
        tk.Button(ctrl, text="DELETE SELECTED", command=self.delete_incoming,
                  bg='#E74C3C', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)
        tk.Button(ctrl, text="EXPORT CSV", command=self.export_incoming_csv,
                  bg='#27AE60', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)

        # Treeview container with scrollbars
        container = tk.Frame(tab, bg='#FFFFFF')
        container.pack(fill='both', expand=True, padx=10, pady=5)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        v = ttk.Scrollbar(container, orient='vertical')
        v.grid(row=0, column=1, sticky='ns')
        h = ttk.Scrollbar(container, orient='horizontal')
        h.grid(row=1, column=0, sticky='ew')

        cols = ('Date', 'Product', 'Quantity (KG)', 'Cost Price (Ksh/KG)', 'Approved By')
        self.in_tree = ttk.Treeview(container, columns=cols, show='headings',
                                    yscrollcommand=v.set, xscrollcommand=h.set, height=14,
                                    selectmode='extended')
        self.in_tree.grid(row=0, column=0, sticky='nsew')
        v.config(command=self.in_tree.yview)
        h.config(command=self.in_tree.xview)

        # Set column widths
        for col, w in zip(cols, [150, 200, 120, 140, 200]):
            self.in_tree.heading(col, text=col)
            self.in_tree.column(col, width=w)

        # Status label and summary bar
        self.in_status = tk.Label(tab, text="", bg='#F5F6FA', fg='green', font=("Segoe UI", 9))
        self.in_status.pack(pady=2)
        self.in_summary = tk.Label(tab, text="", bg='#EBF5FB', fg='#2471A3',
                                   font=("Segoe UI", 9, "bold"), anchor='w', padx=10)
        self.in_summary.pack(fill='x', padx=10, pady=(0, 5))

    # ── OUTGOING TAB ──────────────────────────────
    def _build_outgoing_tab(self):
        tab = self.outgoing_tab

        # Control bar
        ctrl = tk.Frame(tab, bg='#F5F6FA')
        ctrl.pack(fill='x', padx=10, pady=8)
        tk.Button(ctrl, text="REFRESH", command=self.load_outgoing,
                  bg='#3498DB', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)
        tk.Button(ctrl, text="DELETE SELECTED", command=self.delete_outgoing,
                  bg='#E74C3C', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)
        tk.Button(ctrl, text="EXPORT CSV", command=self.export_outgoing_csv,
                  bg='#27AE60', fg='white', font=("Segoe UI", 9, "bold"), relief='flat', padx=10).pack(side='left', padx=4)

        # Treeview container with scrollbars
        container = tk.Frame(tab, bg='#FFFFFF')
        container.pack(fill='both', expand=True, padx=10, pady=5)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        v = ttk.Scrollbar(container, orient='vertical')
        v.grid(row=0, column=1, sticky='ns')
        h = ttk.Scrollbar(container, orient='horizontal')
        h.grid(row=1, column=0, sticky='ew')

        cols = ('Date', 'Product', 'Qty Sold (KG)', 'Selling Price (Ksh/KG)', 'Cost Price (Ksh/KG)', 'Profit (Ksh)')
        self.out_tree = ttk.Treeview(container, columns=cols, show='headings',
                                     yscrollcommand=v.set, xscrollcommand=h.set, height=14,
                                     selectmode='extended')
        self.out_tree.grid(row=0, column=0, sticky='nsew')
        v.config(command=self.out_tree.yview)
        h.config(command=self.out_tree.xview)

        for col, w in zip(cols, [150, 200, 120, 150, 140, 100]):
            self.out_tree.heading(col, text=col)
            self.out_tree.column(col, width=w)

        # Status label and summary bar
        self.out_status = tk.Label(tab, text="", bg='#F5F6FA', fg='green', font=("Segoe UI", 9))
        self.out_status.pack(pady=2)
        self.out_summary = tk.Label(tab, text="", bg='#EAFAF1', fg='#1E8449',
                                    font=("Segoe UI", 9, "bold"), anchor='w', padx=10)
        self.out_summary.pack(fill='x', padx=10, pady=(0, 5))

    # ── LOAD DATA ─────────────────────────────────
    def load_incoming(self):
        # Clear existing treeview rows and ID mapping
        for row in self.in_tree.get_children():
            self.in_tree.delete(row)
        self._in_ids = []

        # Incoming = warehouse OUT transfers that were approved requests sent to this supermarket
        records = list(db.transfers.find({
            "movement_type": "OUT",
            "notes": {"$regex": "Approved request", "$options": "i"}
        }).sort("timestamp", -1))

        # Also include legacy transfers that have a to_email but no movement_type
        legacy = list(db.transfers.find({
            "to_email": {"$exists": True},
            "movement_type": {"$exists": False}
        }).sort("timestamp", -1))

        total_kg = 0.0
        for r in records + legacy:
            # Determine the cost price (from the warehouse product if not directly available)
            cost = r.get('price', r.get('cost_price', 0))
            if cost == 0:
                wp = db.products.find_one({"name": r.get('product_name'), "type": "warehouse"})
                if wp:
                    cost = wp.get('price', 0)

            # Insert into treeview
            iid = self.in_tree.insert('', 'end', values=(
                r['timestamp'].strftime('%Y-%m-%d %H:%M'),
                r.get('product_name', '—'),
                f"{r.get('quantity', 0):.2f}",
                f"Ksh{cost:.2f}",
                r.get('user_email', r.get('from_email', '—'))
            ))
            self._in_ids.append((iid, str(r['_id'])))
            total_kg += r.get('quantity', 0)

        count = len(self._in_ids)
        self.in_status.config(
            text=f"Loaded {count} incoming record(s)",
            fg='green' if count else 'orange'
        )
        self.in_summary.config(
            text=f"   Total received: {total_kg:,.2f} KG  |  Records: {count}"
        )

    def load_outgoing(self):
        # Clear existing treeview rows and ID mapping
        for row in self.out_tree.get_children():
            self.out_tree.delete(row)
        self._out_ids = []

        # Get all sales from the sales collection
        sales = list(db.sales.find({}).sort("timestamp", -1))
        total_kg = 0.0
        total_profit = 0.0

        for s in sales:
            profit = s.get('profit', 0)
            iid = self.out_tree.insert('', 'end', values=(
                s['timestamp'].strftime('%Y-%m-%d %H:%M'),
                s.get('product_name', '—'),
                f"{s.get('quantity_sold', 0):.2f}",
                f"Ksh{s.get('selling_price', 0):.2f}",
                f"Ksh{s.get('cost_price', 0):.2f}",
                f"Ksh{profit:.2f}"
            ))
            self._out_ids.append((iid, str(s['_id'])))
            total_kg += s.get('quantity_sold', 0)
            total_profit += profit

        count = len(sales)
        self.out_status.config(
            text=f"Loaded {count} sale record(s)",
            fg='green' if count else 'orange'
        )
        profit_color = '#1E8449' if total_profit >= 0 else '#C0392B'
        self.out_summary.config(
            text=f"   Total sold: {total_kg:,.2f} KG  |  Total Profit: ${total_profit:,.2f}  |  Records: {count}",
            fg=profit_color
        )

    # ── DELETE ────────────────────────────────────
    def delete_incoming(self):
        # Delete selected incoming (transfer) records from the database
        selected = self.in_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select one or more records to delete")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(selected)} selected record(s)?\n\n"
                                   "NOTE: This removes the log entry only.\n"
                                   "Stock levels will NOT be changed."):
            return
        # Build a map from treeview item ID to MongoDB document ID
        id_map = {iid: mid for iid, mid in self._in_ids}
        deleted = 0
        for iid in selected:
            mid = id_map.get(iid)
            if mid:
                db.transfers.delete_one({"_id": ObjectId(mid)})
                self.in_tree.delete(iid)
                deleted += 1
        self.in_status.config(text=f"Deleted {deleted} record(s)", fg='#E74C3C')
        self.load_incoming()   # refresh the table

    def delete_outgoing(self):
        # Delete selected outgoing (sale) records from the database
        selected = self.out_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select one or more records to delete")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(selected)} selected sale record(s)?\n\n"
                                   "NOTE: This removes the log entry only.\n"
                                   "Stock levels will NOT be changed."):
            return
        id_map = {iid: mid for iid, mid in self._out_ids}
        deleted = 0
        for iid in selected:
            mid = id_map.get(iid)
            if mid:
                db.sales.delete_one({"_id": ObjectId(mid)})
                self.out_tree.delete(iid)
                deleted += 1
        self.out_status.config(text=f"Deleted {deleted} record(s)", fg='#E74C3C')
        self.load_outgoing()   # refresh the table

    # ── EXPORT CSV ────────────────────────────────
    def export_incoming_csv(self):
        # Export the currently displayed incoming records to a CSV file
        rows = [self.in_tree.item(r)['values'] for r in self.in_tree.get_children()]
        if not rows:
            messagebox.showwarning("No Data", "Nothing to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save Incoming Transfers")
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Date', 'Product', 'Quantity (KG)', 'Cost Price ($/KG)', 'Approved By'])
            w.writerows(rows)
        messagebox.showinfo("Exported", f"Saved to {path}")

    def export_outgoing_csv(self):
        # Export the currently displayed outgoing (sale) records to a CSV file
        rows = [self.out_tree.item(r)['values'] for r in self.out_tree.get_children()]
        if not rows:
            messagebox.showwarning("No Data", "Nothing to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save Outgoing Sales")
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Date', 'Product', 'Qty Sold (KG)', 'Selling Price (Ksh/KG)', 'Cost Price (Ksh/KG)', 'Profit (Ksh)'])
            w.writerows(rows)
        messagebox.showinfo("Exported", f"Saved to {path}")