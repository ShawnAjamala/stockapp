import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_all_movements, get_movements_by_type
from bson import ObjectId
from pymongo import MongoClient
import csv
from datetime import datetime

# Direct DB access for deletes
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")
db = client.supermarket_storage


class WarehouseTransfers(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user
        self.refresh_callback = refresh_callback
        self.configure(bg='#F5F6FA')
        self._row_ids = []  # maps treeview iid → MongoDB _id

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="WAREHOUSE TRANSFERS (IN / OUT)",
                 font=("Segoe UI", 18, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        control = tk.Frame(self, bg='#F5F6FA')
        control.pack(fill='x', padx=10, pady=5)

        tk.Label(control, text="Filter by Type:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(control, textvariable=self.filter_var,
                                 values=["All", "IN", "OUT"], width=10, state='readonly')
        filter_cb.pack(side='left', padx=5)
        filter_cb.bind('<<ComboboxSelected>>', lambda e: self.load_data())

        tk.Button(control, text="REFRESH", command=self.load_data,
                  bg='#3498DB', fg='white').pack(side='left', padx=5)
        tk.Button(control, text="DELETE SELECTED", command=self.delete_selected,
                  bg='#E74C3C', fg='white', font=("Segoe UI", 9, "bold")).pack(side='left', padx=5)
        tk.Button(control, text="EXPORT CSV", command=self.export_csv,
                  bg='#27AE60', fg='white').pack(side='left', padx=5)

        # Treeview with scrollbars
        tree_container = tk.Frame(self, bg='#FFFFFF')
        tree_container.pack(fill='both', expand=True, padx=10, pady=5)
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(tree_container, orient='vertical')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(tree_container, orient='horizontal')
        h_scroll.grid(row=1, column=0, sticky='ew')

        columns = ('Date', 'Product', 'Type', 'Quantity (KG)', 'Notes', 'Recorded By')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set,
                                 selectmode='extended')   # allows multi-select
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.column('Product', width=180)
        self.tree.column('Notes', width=200)

        self.status_label = tk.Label(self, text="", bg='#F5F6FA', fg='green')
        self.status_label.pack(pady=5)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._row_ids = []

        filter_type = self.filter_var.get()
        movements = get_all_movements() if filter_type == "All" else get_movements_by_type(filter_type)

        if not movements:
            self.status_label.config(text="No movements found", fg='orange')
            return

        for m in movements:
            mov_type = m.get('movement_type')
            if not mov_type:
                notes = m.get('notes', '').lower()
                if 'initial stock' in notes or 'added' in notes:
                    mov_type = 'IN'
                elif 'sent to' in notes or 'approved request' in notes:
                    mov_type = 'OUT'
                else:
                    mov_type = 'UNKNOWN'

            iid = self.tree.insert('', 'end', values=(
                m['timestamp'].strftime('%Y-%m-%d %H:%M'),
                m['product_name'],
                mov_type,
                f"{m['quantity']:.2f}",
                m.get('notes', ''),
                m.get('user_email', 'system')
            ))
            self._row_ids.append((iid, str(m['_id'])))

        count = len(self._row_ids)
        self.status_label.config(text=f"Loaded {count} movements", fg='green')
        if self.refresh_callback:
            self.refresh_callback()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select one or more records to delete")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(selected)} selected record(s)?\n\n"
                                   "NOTE: This removes the log entry only.\n"
                                   "Stock levels will NOT be changed."):
            return

        id_map = {iid: mid for iid, mid in self._row_ids}
        deleted = 0
        for iid in selected:
            mid = id_map.get(iid)
            if mid:
                db.transfers.delete_one({"_id": ObjectId(mid)})
                self.tree.delete(iid)
                deleted += 1

        self.status_label.config(text=f"Deleted {deleted} record(s)", fg='#E74C3C')
        # Rebuild id map after deletion
        self._row_ids = [(iid, mid) for iid, mid in self._row_ids
                         if iid not in {i for i in selected}]

    def export_csv(self):
        filter_type = self.filter_var.get()
        movements = get_all_movements() if filter_type == "All" else get_movements_by_type(filter_type)

        if not movements:
            messagebox.showwarning("No Data", "Nothing to export")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Warehouse Transfers"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Product', 'Type', 'Quantity (KG)', 'Notes', 'Recorded By'])
                for m in movements:
                    mov_type = m.get('movement_type')
                    if not mov_type:
                        notes = m.get('notes', '').lower()
                        mov_type = 'IN' if ('initial stock' in notes or 'added' in notes) else 'OUT'
                    writer.writerow([
                        m['timestamp'].strftime('%Y-%m-%d %H:%M'),
                        m['product_name'],
                        mov_type,
                        f"{m['quantity']:.2f}",
                        m.get('notes', ''),
                        m.get('user_email', 'system')
                    ])
            messagebox.showinfo("Export Successful", f"Saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))