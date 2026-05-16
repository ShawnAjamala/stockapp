import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    get_all_warehouse_products,
    get_users_by_role,
    record_stock_movement,
    create_transfer,
    get_pending_requests_for_warehouse,
    create_notification,
    get_user_notifications,
    mark_notification_as_read,
    delete_notification,
    get_unread_notifications_count,
    alerts,
    receive_stock_from_warehouse   # <-- Import this
)
from bson import ObjectId

class WarehouseSend(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user
        self.refresh_callback = refresh_callback
        self.configure(bg='#F5F6FA')
        self.product_dict = {}
        self.pending_requests = []
        self.filled_request_id = None

        self.create_widgets()
        self.load_warehouse_products()
        self.load_pending_requests()
        self.update_notification_badge()

    # ------------------ UI creation (unchanged) ------------------
    def create_widgets(self):
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SEND STOCK TO SUPERMARKET", font=("Segoe UI", 18, "bold"),
                 bg='#FFFFFF', fg='#E67E22').pack(side='left', padx=20, pady=15)

        self.notify_btn = tk.Button(header, text="NOTIFICATIONS (0)", command=self.show_notifications,
                                    bg='#C0392B', fg='white', font=("Segoe UI", 9, "bold"),
                                    relief='flat', padx=15, pady=5)
        self.notify_btn.pack(side='right', padx=20)

        main = tk.Frame(self, bg='#F5F6FA')
        main.pack(fill='both', expand=True, padx=10, pady=10)

        # LEFT: Send form
        left = tk.LabelFrame(main, text="SEND STOCK FORM", font=("Segoe UI", 11, "bold"),
                             bg='#FFFFFF', fg='#E67E22')
        left.pack(side='left', fill='both', expand=True, padx=(0,5))

        form = tk.Frame(left, bg='#FFFFFF')
        form.pack(pady=15, padx=15)

        tk.Label(form, text="Product:").grid(row=0, column=0, sticky='w', pady=5)
        self.product_cb = ttk.Combobox(form, width=30, state='readonly')
        self.product_cb.grid(row=0, column=1, pady=5)
        self.product_cb.bind('<<ComboboxSelected>>', self.on_product_select)

        tk.Label(form, text="Available (KG):").grid(row=0, column=2, padx=10, pady=5)
        self.avail_label = tk.Label(form, text="0", fg='green')
        self.avail_label.grid(row=0, column=3, pady=5)

        tk.Label(form, text="Price/KG ($):").grid(row=1, column=0, sticky='w', pady=5)
        self.price_label = tk.Label(form, text="$0.00", fg='#E67E22')
        self.price_label.grid(row=1, column=1, pady=5)

        tk.Label(form, text="Supermarket:").grid(row=1, column=2, padx=10, pady=5)
        supermarkets = get_users_by_role("supermarket admin")
        self.supermarket_cb = ttk.Combobox(form, values=[s['email'] for s in supermarkets],
                                           width=25, state='readonly')
        self.supermarket_cb.grid(row=1, column=3, pady=5)

        tk.Label(form, text="Quantity (KG):").grid(row=2, column=0, sticky='w', pady=5)
        self.qty_entry = tk.Entry(form, width=15)
        self.qty_entry.grid(row=2, column=1, pady=5)
        self.qty_entry.bind('<KeyRelease>', self.calc_total)

        tk.Label(form, text="Total Value:").grid(row=2, column=2, padx=10, pady=5)
        self.total_label = tk.Label(form, text="$0.00", fg='green')
        self.total_label.grid(row=2, column=3, pady=5)

        self.send_btn = tk.Button(form, text="SEND STOCK", command=self.send_stock,
                                  bg='#27AE60', fg='white', width=20)
        self.send_btn.grid(row=3, column=0, columnspan=4, pady=15)

        # RIGHT: Pending requests
        right = tk.LabelFrame(main, text="PENDING REQUESTS", font=("Segoe UI", 11, "bold"),
                              bg='#FFFFFF', fg='#E67E22')
        right.pack(side='right', fill='both', expand=True, padx=(5,0))

        req_frame = tk.Frame(right, bg='#FFFFFF')
        req_frame.pack(fill='both', expand=True, padx=10, pady=10)
        scroll = tk.Scrollbar(req_frame)
        scroll.pack(side='right', fill='y')
        self.req_listbox = tk.Listbox(req_frame, yscrollcommand=scroll.set, height=12)
        self.req_listbox.pack(side='left', fill='both', expand=True)
        scroll.config(command=self.req_listbox.yview)

        btn_frame = tk.Frame(right, bg='#FFFFFF')
        btn_frame.pack(fill='x', pady=5)
        self.approve_btn = tk.Button(btn_frame, text="APPROVE & FILL FORM", command=self.approve_and_fill,
                                     bg='#F39C12', fg='white', width=18)
        self.approve_btn.pack(side='left', padx=10)
        self.refresh_btn = tk.Button(btn_frame, text="REFRESH REQUESTS", command=self.load_pending_requests,
                                     bg='#3498DB', fg='white', width=18)
        self.refresh_btn.pack(side='right', padx=10)

        self.status_label = tk.Label(right, text="", bg='#FFFFFF', fg='green')
        self.status_label.pack(pady=5)

    # ------------------ Helpers (unchanged) ------------------
    def update_notification_badge(self):
        count = get_unread_notifications_count(self.user['email'])
        self.notify_btn.config(text=f"NOTIFICATIONS ({count})" if count else "NOTIFICATIONS")

    def show_notifications(self):
        notifs = get_user_notifications(self.user['email'])
        win = tk.Toplevel(self)
        win.title("Notifications")
        win.geometry("500x400")
        win.configure(bg='#FFFFFF')
        win.resizable(False, False)

        tk.Label(win, text="NOTIFICATIONS", font=("Arial", 14, "bold"),
                 bg='#FFFFFF', fg='#E67E22').pack(pady=10)

        frame = tk.Frame(win, bg='#FFFFFF')
        frame.pack(fill='both', expand=True, padx=10, pady=5)

        canvas = tk.Canvas(frame, bg='#FFFFFF', highlightthickness=0)
        scroll = tk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg='#FFFFFF')

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        if not notifs:
            tk.Label(inner, text="No notifications", bg='#FFFFFF').pack(pady=20)
        else:
            for n in notifs:
                bg = '#FEF9E7' if not n['read'] else '#FFFFFF'
                f = tk.Frame(inner, bg=bg, relief='solid', bd=1)
                f.pack(fill='x', pady=2, padx=5)
                tk.Label(f, text=n['title'], font=("Arial", 9, "bold"),
                         bg=bg, fg='#E67E22').pack(anchor='w', padx=10, pady=(5,0))
                tk.Label(f, text=n['message'], bg=bg, wraplength=400).pack(anchor='w', padx=10, pady=2)
                btnf = tk.Frame(f, bg=bg)
                btnf.pack(fill='x', pady=5, padx=10)
                if not n['read']:
                    tk.Button(btnf, text="Mark Read", command=lambda nid=str(n['_id']): self._mark_read(nid, win),
                              bg='#3498DB', fg='white', font=("Arial",8)).pack(side='left', padx=2)
                tk.Button(btnf, text="Delete", command=lambda nid=str(n['_id']): self._delete_notif(nid, win),
                          bg='#E74C3C', fg='white', font=("Arial",8)).pack(side='left', padx=2)

        tk.Button(win, text="CLOSE", command=win.destroy, bg='#95A5A6', fg='white').pack(pady=10)

    def _mark_read(self, nid, win):
        mark_notification_as_read(nid)
        win.destroy()
        self.show_notifications()
        self.update_notification_badge()

    def _delete_notif(self, nid, win):
        delete_notification(nid)
        win.destroy()
        self.show_notifications()
        self.update_notification_badge()

    def load_warehouse_products(self):
        prods = get_all_warehouse_products()
        self.product_dict = {p['name']: p for p in prods}
        self.product_cb['values'] = list(self.product_dict.keys())

    def on_product_select(self, event):
        name = self.product_cb.get()
        if name in self.product_dict:
            p = self.product_dict[name]
            self.avail_label.config(text=f"{p['quantity']:.2f}")
            self.price_label.config(text=f"${p['price']:.2f}")
            self.calc_total()

    def calc_total(self, event=None):
        try:
            qty = float(self.qty_entry.get())
            name = self.product_cb.get()
            if name in self.product_dict:
                price = self.product_dict[name]['price']
                self.total_label.config(text=f"${qty * price:.2f}")
            else:
                self.total_label.config(text="$0.00")
        except:
            self.total_label.config(text="$0.00")

    def load_pending_requests(self):
        self.req_listbox.delete(0, tk.END)
        self.pending_requests = get_pending_requests_for_warehouse(self.user['email'])
        for req in self.pending_requests:
            display = f"{req['product_name']} – {req['quantity']:.2f} KG from {req['supermarket_email']}"
            self.req_listbox.insert(tk.END, display)
        if not self.pending_requests:
            self.req_listbox.insert(tk.END, "No pending requests")
            self.approve_btn.config(state='disabled')
        else:
            self.approve_btn.config(state='normal')

    def approve_and_fill(self):
        sel = self.req_listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a request first")
            return
        if sel[0] >= len(self.pending_requests):
            return
        req = self.pending_requests[sel[0]]
        self.product_cb.set(req['product_name'])
        self.supermarket_cb.set(req['supermarket_email'])
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, str(req['quantity']))
        self.on_product_select(None)
        self.status_label.config(text=f"Form filled for request from {req['supermarket_email']}", fg='green')
        self.filled_request_id = str(req['_id'])

    # ---------- FIXED send_stock: also updates supermarket inventory ----------
    def send_stock(self):
        product_name = self.product_cb.get()
        supermarket_email = self.supermarket_cb.get()
        qty_str = self.qty_entry.get().strip()

        if not product_name or not supermarket_email or not qty_str:
            messagebox.showerror("Error", "Please fill all fields (use 'Approve & Fill' first)")
            return
        try:
            qty = float(qty_str)
        except:
            messagebox.showerror("Error", "Invalid quantity")
            return

        if product_name not in self.product_dict:
            messagebox.showerror("Error", "Product not found")
            return
        avail = self.product_dict[product_name]['quantity']
        if qty > avail:
            messagebox.showerror("Error", f"Insufficient stock. Only {avail:.2f} KG available")
            return

        # 1. Deduct from warehouse
        ok, msg = record_stock_movement(product_name, "OUT", qty,
                                        f"Sent to {supermarket_email} (direct send)",
                                        self.user['email'])
        if not ok:
            messagebox.showerror("Error", msg)
            return

        # 2. Add stock to supermarket (using receive_stock_from_warehouse)
        warehouse_product = self.product_dict[product_name]
        success, receive_msg = receive_stock_from_warehouse(
            product_name, qty, warehouse_product['price'], self.user['email']
        )
        if not success:
            messagebox.showerror("Error", f"Failed to add stock to supermarket: {receive_msg}")
            # Optionally rollback warehouse deduction? For simplicity, just show error.
            return

        # 3. Record transfer (so supermarket sees it in "Stock Received")
        create_transfer(self.user['email'], supermarket_email, product_name, qty)

        # 4. Mark request as processed if this send came from an approved request
        if self.filled_request_id:
            alerts.update_one({"_id": ObjectId(self.filled_request_id)},
                              {"$set": {"processed": True, "read": True}})
            self.filled_request_id = None
            self.load_pending_requests()

        # 5. Notify supermarket
        create_notification(supermarket_email, "Stock Received",
                            f"{qty:.2f} KG of {product_name} has been sent from warehouse", "stock_received")

        messagebox.showinfo("Success", f"Sent {qty:.2f} KG of {product_name} to {supermarket_email}")

        # 6. Clear form
        self.product_cb.set('')
        self.supermarket_cb.set('')
        self.qty_entry.delete(0, tk.END)
        self.total_label.config(text="$0.00")
        self.avail_label.config(text="0")
        self.price_label.config(text="$0.00")
        self.status_label.config(text="")
        self.load_warehouse_products()

        # 7. Refresh dashboard stats
        if self.refresh_callback:
            self.refresh_callback()