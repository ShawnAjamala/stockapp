import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_all_movements, get_movements_by_type
from bson import ObjectId
from pymongo import MongoClient
import csv
from datetime import datetime

# Direct DB access for deletes (separate connection for delete operations)
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")
db = client.supermarket_storage

# Warehouse transfers page: displays all stock movements (IN/OUT) with filter, delete, and CSV export
class WarehouseTransfers(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user                        # logged‑in warehouse admin
        self.refresh_callback = refresh_callback  # callback to refresh dashboard stats
        self.configure(bg='#F5F6FA')
        self._row_ids = []                      # list of tuples (treeview iid, MongoDB _id)

        self.create_widgets()
        self.load_data()

    # Build the user interface (header, filter controls, Treeview with scrollbars)
    def create_widgets(self):
        # Header with title
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="WAREHOUSE TRANSFERS (IN / OUT)",
                 font=("Segoe UI", 18, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        # Control bar: filter, refresh, delete selected, export CSV
        control = tk.Frame(self, bg='#F5F6FA')
        control.pack(fill='x', padx=10, pady=5)

        # Filter by type combobox
        tk.Label(control, text="Filter by Type:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(control, textvariable=self.filter_var,
                                 values=["All", "IN", "OUT"], width=10, state='readonly')
        filter_cb.pack(side='left', padx=5)
        filter_cb.bind('<<ComboboxSelected>>', lambda e: self.load_data())   # refresh on filter change

        # Refresh button – manually reload data from database
        tk.Button(control, text="REFRESH", command=self.load_data,
                  bg='#3498DB', fg='white').pack(side='left', padx=5)
        # Delete selected records button
        tk.Button(control, text="DELETE SELECTED", command=self.delete_selected,
                  bg='#E74C3C', fg='white', font=("Segoe UI", 9, "bold")).pack(side='left', padx=5)
        # Export to CSV button
        tk.Button(control, text="EXPORT CSV", command=self.export_csv,
                  bg='#27AE60', fg='white').pack(side='left', padx=5)

        # Treeview container with both vertical and horizontal scrollbars
        tree_container = tk.Frame(self, bg='#FFFFFF')
        tree_container.pack(fill='both', expand=True, padx=10, pady=5)
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(tree_container, orient='vertical')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(tree_container, orient='horizontal')
        h_scroll.grid(row=1, column=0, sticky='ew')

        # Define columns for the transfers table
        columns = ('Date', 'Product', 'Type', 'Quantity (KG)', 'Notes', 'Recorded By')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set,
                                 selectmode='extended')   # allow multiple row selection
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        # Set column headings and default widths
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.column('Product', width=180)   # wider product column
        self.tree.column('Notes', width=200)     # wider notes column

        # Status label for feedback messages
        self.status_label = tk.Label(self, text="", bg='#F5F6FA', fg='green')
        self.status_label.pack(pady=5)

    # Load data from database according to the current filter and populate the Treeview
    def load_data(self):
        # Clear existing rows and id mapping
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._row_ids = []

        # Fetch movements based on filter type
        filter_type = self.filter_var.get()
        if filter_type == "All":
            movements = get_all_movements()
        else:
            movements = get_movements_by_type(filter_type)

        if not movements:
            self.status_label.config(text="No movements found", fg='orange')
            return

        # Iterate over each movement and insert into treeview
        for m in movements:
            # Determine movement type (handle missing or legacy fields)
            mov_type = m.get('movement_type')
            if not mov_type:
                notes = m.get('notes', '').lower()
                if 'initial stock' in notes or 'added' in notes:
                    mov_type = 'IN'
                elif 'sent to' in notes or 'approved request' in notes:
                    mov_type = 'OUT'
                else:
                    mov_type = 'UNKNOWN'

            # Insert row and store mapping between treeview item id and MongoDB document id
            iid = self.tree.insert('', 'end', values=(
                m['timestamp'].strftime('%Y-%m-%d %H:%M'),   # formatted date/time
                m['product_name'],
                mov_type,
                f"{m['quantity']:.2f}",
                m.get('notes', ''),
                m.get('user_email', 'system')
            ))
            self._row_ids.append((iid, str(m['_id'])))

        count = len(self._row_ids)
        self.status_label.config(text=f"Loaded {count} movements", fg='green')
        # Notify dashboard that data has changed (so it can refresh stats)
        if self.refresh_callback:
            self.refresh_callback()

    # Delete the currently selected rows from the database and the Treeview
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select one or more records to delete")
            return
        # Confirm deletion with the user
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(selected)} selected record(s)?\n\n"
                                   "NOTE: This removes the log entry only.\n"
                                   "Stock levels will NOT be changed."):
            return

        # Build a map from treeview item id to MongoDB document id
        id_map = {iid: mid for iid, mid in self._row_ids}
        deleted = 0
        # Delete each selected record from MongoDB and remove from treeview
        for iid in selected:
            mid = id_map.get(iid)
            if mid:
                db.transfers.delete_one({"_id": ObjectId(mid)})   # permanent deletion
                self.tree.delete(iid)
                deleted += 1

        self.status_label.config(text=f"Deleted {deleted} record(s)", fg='#E74C3C')
        # Update the internal id list by removing deleted items
        self._row_ids = [(iid, mid) for iid, mid in self._row_ids
                         if iid not in {i for i in selected}]

    # Export the currently displayed movements (respecting the filter) to a CSV file
    def export_csv(self):
        filter_type = self.filter_var.get()
        if filter_type == "All":
            movements = get_all_movements()
        else:
            movements = get_movements_by_type(filter_type)

        if not movements:
            messagebox.showwarning("No Data", "Nothing to export")
            return

        # Ask user for file save location
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
                # Write header row
                writer.writerow(['Date', 'Product', 'Type', 'Quantity (KG)', 'Notes', 'Recorded By'])
                # Write each movement as a row
                for m in movements:
                    # Infer movement type if missing (same logic as in load_data)
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