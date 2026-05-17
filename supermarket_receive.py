import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    get_all_warehouse_products,
    get_all_supermarket_products,
    update_selling_price,
    create_stock_request,
    get_users_by_role
)

# Supermarket page for requesting stock (multi‑item cart) and viewing/updating inventory
class SupermarketReceive(tk.Frame):
    def __init__(self, parent, user, refresh_callback=None):
        super().__init__(parent)
        self.user = user                        # logged‑in user object
        self.refresh_callback = refresh_callback  # function to refresh dashboard stats
        self.configure(bg='#F5F6FA')
        self.cart = []                          # list of items to request: {name, quantity}
        self.warehouse_products = {}            # warehouse products (name -> details)
        self.supermarket_products = {}          # current supermarket inventory

        self.create_widgets()
        self.load_warehouse_products()
        self.load_supermarket_products()

    # Build the GUI layout
    def create_widgets(self):
        # Header with title
        header = tk.Frame(self, bg='#FFFFFF', height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="REQUEST STOCK & MANAGE INVENTORY",
                 font=("Segoe UI", 18, "bold"), bg='#FFFFFF', fg='#E67E22').pack(pady=15)

        # Two columns: left = request cart, right = inventory & price update
        left = tk.Frame(self, bg='#F5F6FA')
        left.pack(side='left', fill='both', expand=True, padx=10)
        right = tk.Frame(self, bg='#F5F6FA')
        right.pack(side='right', fill='both', expand=True, padx=10)

        # --- LEFT: Multi‑item request cart ---
        cart_frame = tk.LabelFrame(left, text="MULTI-ITEM REQUEST", font=("Segoe UI", 11, "bold"),
                                   bg='#FFFFFF', fg='#E67E22')
        cart_frame.pack(fill='both', expand=True, pady=5)

        # Form to add a product to the cart
        add_frame = tk.Frame(cart_frame, bg='#FFFFFF')
        add_frame.pack(fill='x', pady=10, padx=10)

        tk.Label(add_frame, text="Product:").grid(row=0, column=0, padx=5, pady=5)
        self.product_cb = ttk.Combobox(add_frame, width=25, state='readonly')
        self.product_cb.grid(row=0, column=1, padx=5, pady=5)
        self.product_cb.bind('<<ComboboxSelected>>', self.on_product_select)

        tk.Label(add_frame, text="Avail (KG):").grid(row=0, column=2, padx=5, pady=5)
        self.avail_label = tk.Label(add_frame, text="0", fg='green')
        self.avail_label.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(add_frame, text="Cost/KG:").grid(row=1, column=0, padx=5, pady=5)
        self.price_label = tk.Label(add_frame, text="$0.00", fg='#E67E22')
        self.price_label.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Qty (KG):").grid(row=1, column=2, padx=5, pady=5)
        self.qty_entry = tk.Entry(add_frame, width=12)
        self.qty_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(add_frame, text="ADD TO CART", command=self.add_to_cart,
                  bg='#27AE60', fg='white').grid(row=2, column=0, columnspan=4, pady=10)

        # Listbox to display current cart items
        cart_list_frame = tk.Frame(cart_frame, bg='#FFFFFF')
        cart_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        scroll = tk.Scrollbar(cart_list_frame)
        scroll.pack(side='right', fill='y')
        self.cart_listbox = tk.Listbox(cart_list_frame, yscrollcommand=scroll.set, height=8)
        self.cart_listbox.pack(side='left', fill='both', expand=True)
        scroll.config(command=self.cart_listbox.yview)

        # Remove button for the selected cart item
        tk.Button(cart_frame, text="REMOVE SELECTED", command=self.remove_from_cart,
                  bg='#E74C3C', fg='white').pack(pady=5)

        # Warehouse employee selection dropdown (try "warehouse admin" first, fallback to "warehouse")
        wh_frame = tk.Frame(cart_frame, bg='#FFFFFF')
        wh_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(wh_frame, text="Warehouse Employee:").pack(side='left')
        warehouses = get_users_by_role("warehouse admin")
        if not warehouses:
            warehouses = get_users_by_role("warehouse")
        self.warehouse_cb = ttk.Combobox(wh_frame, values=[w['email'] for w in warehouses],
                                         width=25, state='readonly')
        self.warehouse_cb.pack(side='left', padx=5)

        # Send request button
        tk.Button(cart_frame, text="SEND REQUEST", command=self.send_request,
                  bg='#F39C12', fg='white', font=("Segoe UI", 10, "bold")).pack(pady=10)

        # --- RIGHT: Current inventory and selling price update ---
        inv_frame = tk.LabelFrame(right, text="CURRENT INVENTORY", font=("Segoe UI", 11, "bold"),
                                  bg='#FFFFFF', fg='#E67E22')
        inv_frame.pack(fill='both', expand=True, pady=5)

        # Search bar for inventory
        search_frame = tk.Frame(inv_frame, bg='#FFFFFF')
        search_frame.pack(fill='x', pady=5, padx=10)
        tk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="GO", command=self.search_inventory,
                  bg='#3498DB', fg='white').pack(side='left')
        tk.Button(search_frame, text="REFRESH", command=self.load_supermarket_products,
                  bg='#95A5A6', fg='white').pack(side='left', padx=2)

        # Treeview to display supermarket products
        tree_container = tk.Frame(inv_frame, bg='#FFFFFF')
        tree_container.pack(fill='both', expand=True, padx=10, pady=5)
        scroll_inv = ttk.Scrollbar(tree_container)
        scroll_inv.pack(side='right', fill='y')
        columns = ('Name', 'Stock', 'Cost', 'Selling')
        self.inv_tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                     yscrollcommand=scroll_inv.set, height=12)
        scroll_inv.config(command=self.inv_tree.yview)
        self.inv_tree.heading('Name', text='Product')
        self.inv_tree.heading('Stock', text='KG')
        self.inv_tree.heading('Cost', text='Cost $/KG')
        self.inv_tree.heading('Selling', text='Selling $/KG')
        self.inv_tree.column('Name', width=150)
        self.inv_tree.column('Stock', width=70)
        self.inv_tree.column('Cost', width=80)
        self.inv_tree.column('Selling', width=80)
        self.inv_tree.pack(side='left', fill='both', expand=True)

        # Panel for updating the selling price of a supermarket product
        price_frame = tk.LabelFrame(right, text="UPDATE SELLING PRICE", font=("Segoe UI", 10, "bold"),
                                    bg='#FFFFFF', fg='#E67E22')
        price_frame.pack(fill='x', pady=5)

        price_inner = tk.Frame(price_frame, bg='#FFFFFF')
        price_inner.pack(pady=10, padx=10)
        tk.Label(price_inner, text="Product:").grid(row=0, column=0, padx=5, pady=5)
        self.price_product_cb = ttk.Combobox(price_inner, width=20, state='readonly')
        self.price_product_cb.grid(row=0, column=1, padx=5, pady=5)
        self.price_product_cb.bind('<<ComboboxSelected>>', self.on_price_product_select)

        tk.Label(price_inner, text="New Price ($/KG):").grid(row=0, column=2, padx=5, pady=5)
        self.new_price_entry = tk.Entry(price_inner, width=10)
        self.new_price_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(price_inner, text="Profit/KG:").grid(row=1, column=0, padx=5, pady=5)
        self.profit_preview = tk.Label(price_inner, text="$0.00", fg='green')
        self.profit_preview.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(price_inner, text="UPDATE", command=self.update_selling_price,
                  bg='#3498DB', fg='white').grid(row=1, column=2, columnspan=2, pady=5)
        self.new_price_entry.bind('<KeyRelease>', self.update_profit_preview)

    # ------------------ Data Loading ------------------
    def load_warehouse_products(self):
        # Get all warehouse products from the database
        prods = get_all_warehouse_products()
        # Deduplicate by name: keep the entry with the highest quantity.
        # Do NOT sum quantities – the same product name can appear in multiple DB rows
        # (e.g. different batches), but summing them would double the displayed stock.
        deduplicated = {}
        for p in prods:
            name = p['name']
            if name not in deduplicated or p['quantity'] > deduplicated[name]['quantity']:
                deduplicated[name] = {
                    'name': name,
                    'quantity': p['quantity'],
                    'price': p['price']
                }
        self.warehouse_products = deduplicated
        self.product_cb['values'] = list(self.warehouse_products.keys())

    def load_supermarket_products(self):
        # Refresh the inventory treeview with current supermarket products
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        prods = get_all_supermarket_products()
        self.supermarket_products = {p['name']: p for p in prods}
        self.price_product_cb['values'] = list(self.supermarket_products.keys())
        for p in prods:
            self.inv_tree.insert('', 'end', values=(
                p['name'],
                f"{p['quantity']:.1f}",
                f"${p.get('cost_price', 0):.2f}",
                f"${p.get('selling_price', 0):.2f}"
            ))

    def search_inventory(self):
        # Filter inventory treeview by product name
        kw = self.search_entry.get().strip().lower()
        self.inv_tree.delete(*self.inv_tree.get_children())
        for name, p in self.supermarket_products.items():
            if kw in name.lower():
                self.inv_tree.insert('', 'end', values=(
                    name,
                    f"{p['quantity']:.1f}",
                    f"${p.get('cost_price', 0):.2f}",
                    f"${p.get('selling_price', 0):.2f}"
                ))

    # Called when a product is selected in the request combobox
    def on_product_select(self, event):
        name = self.product_cb.get()
        if name in self.warehouse_products:
            p = self.warehouse_products[name]
            self.avail_label.config(text=f"{p['quantity']:.2f}")
            self.price_label.config(text=f"${p['price']:.2f}")

    # ---------- Cart methods ----------
    def add_to_cart(self):
        # Add the current product/quantity to the request cart
        name = self.product_cb.get()
        if not name:
            messagebox.showerror("Error", "Select a product")
            return
        qty_str = self.qty_entry.get().strip()
        if not qty_str:
            messagebox.showerror("Error", "Enter quantity")
            return
        try:
            qty = float(qty_str)
        except:
            messagebox.showerror("Error", "Invalid quantity")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity >0 required")
            return
        if name not in self.warehouse_products:
            messagebox.showerror("Error", "Product not found")
            return
        avail = self.warehouse_products[name]['quantity']
        if qty > avail:
            messagebox.showerror("Error", f"Only {avail:.2f} KG available")
            return
        # If product already in cart, update its quantity (no duplicate entries)
        for item in self.cart:
            if item['name'] == name:
                new_qty = item['quantity'] + qty
                if new_qty > avail:
                    messagebox.showerror("Error", f"Total request {new_qty:.2f} KG exceeds {avail:.2f}")
                    return
                item['quantity'] = new_qty
                self.refresh_cart()
                self.qty_entry.delete(0, tk.END)
                return
        # Otherwise add new item
        self.cart.append({'name': name, 'quantity': qty})
        self.refresh_cart()
        self.qty_entry.delete(0, tk.END)

    def remove_from_cart(self):
        # Remove the selected cart item
        sel = self.cart_listbox.curselection()
        if sel:
            del self.cart[sel[0]]
            self.refresh_cart()

    def refresh_cart(self):
        # Update the cart listbox display
        self.cart_listbox.delete(0, tk.END)
        for item in self.cart:
            self.cart_listbox.insert(tk.END, f"{item['name']} – {item['quantity']:.2f} KG")

    def send_request(self):
        # Send the entire cart as separate stock requests to the selected warehouse employee
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty")
            return
        wh_email = self.warehouse_cb.get()
        if not wh_email:
            messagebox.showerror("Error", "Select a warehouse employee")
            return
        success = True
        for item in self.cart:
            ok, msg = create_stock_request(item['name'], item['quantity'], self.user['email'], wh_email)
            if not ok:
                success = False
                messagebox.showerror("Error", f"Failed for {item['name']}: {msg}")
                break
        if success:
            messagebox.showinfo("Success", f"Request for {len(self.cart)} item(s) sent to {wh_email}")
            self.cart.clear()
            self.refresh_cart()
            if self.refresh_callback:
                self.refresh_callback()   # update dashboard stats

    # ---------- Selling price update methods ----------
    def on_price_product_select(self, event):
        # Populate the new price field with the current selling price
        name = self.price_product_cb.get()
        if name in self.supermarket_products:
            cur = self.supermarket_products[name].get('selling_price', 0)
            self.new_price_entry.delete(0, tk.END)
            self.new_price_entry.insert(0, f"{cur:.2f}")
            self.update_profit_preview()

    def update_profit_preview(self, event=None):
        # Show the profit per KG based on the new price and cost price
        name = self.price_product_cb.get()
        if not name or name not in self.supermarket_products:
            self.profit_preview.config(text="$0.00")
            return
        cost = self.supermarket_products[name].get('cost_price', 0)
        try:
            new_price = float(self.new_price_entry.get())
        except:
            new_price = 0
        profit = new_price - cost
        self.profit_preview.config(text=f"${profit:.2f}", fg='green' if profit >= 0 else 'red')

    def update_selling_price(self):
        # Apply the new selling price to the selected supermarket product
        name = self.price_product_cb.get()
        if not name:
            messagebox.showerror("Error", "Select a product")
            return
        try:
            new_price = float(self.new_price_entry.get())
        except:
            messagebox.showerror("Error", "Invalid price")
            return
        if new_price <= 0:
            messagebox.showerror("Error", "Price must be positive")
            return
        ok, msg = update_selling_price(name, new_price)
        if ok:
            messagebox.showinfo("Success", msg)
            self.load_supermarket_products()          # refresh inventory display
            if self.refresh_callback:
                self.refresh_callback()               # update dashboard
        else:
            messagebox.showerror("Error", msg)