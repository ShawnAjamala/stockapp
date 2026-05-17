# Imports for databases required
from pymongo import MongoClient
from datetime import datetime
import hashlib

# Database connection
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")
db = client.supermarket_storage

# Collections
users = db.users
products = db.products
transfers = db.transfers
sales = db.sales
alerts = db.alerts
notifications = db.notifications          # user‑specific notifications

# Fixed role passwords
SUPERMARKET_PASSWORD = "000000"
WAREHOUSE_PASSWORD = "111111"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------- USER OPERATIONS --------------------
def create_user(email, password, fullname, role):
    user_data = {
        "email": email,
        "password": hash_password(password),
        "fullname": fullname,
        "role": role,
        "created_at": datetime.now()
    }
    return users.insert_one(user_data)

def find_user_by_email(email):
    return users.find_one({"email": email})

def find_user_by_email_and_password(email, password):
    return users.find_one({"email": email, "password": hash_password(password)})

def get_all_users():
    return list(users.find({}))

def get_users_by_role(role):
    return list(users.find({"role": role}))

# ==================== USER NOTIFICATIONS ====================
def create_notification(user_email, title, message, notification_type):
    try:
        notification_data = {
            "user_email": user_email,
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now(),
            "read": False
        }
        notifications.insert_one(notification_data)
        return True, "Notification created"
    except Exception as e:
        print(f"Error creating notification: {e}")
        return False, str(e)

def get_user_notifications(user_email):
    try:
        return list(notifications.find({"user_email": user_email}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []

def get_unread_notifications_count(user_email):
    try:
        return notifications.count_documents({"user_email": user_email, "read": False})
    except Exception as e:
        return 0

def mark_notification_as_read(notification_id):
    try:
        from bson import ObjectId
        notifications.update_one({"_id": ObjectId(notification_id)}, {"$set": {"read": True}})
        return True
    except Exception as e:
        return False

def delete_notification(notification_id):
    try:
        from bson import ObjectId
        notifications.delete_one({"_id": ObjectId(notification_id)})
        return True, "Notification deleted"
    except Exception as e:
        return False, str(e)

def delete_all_notifications(user_email):
    try:
        result = notifications.delete_many({"user_email": user_email})
        return True, f"Deleted {result.deleted_count} notifications"
    except Exception as e:
        return False, str(e)

def mark_all_notifications_as_read(user_email):
    try:
        notifications.update_many({"user_email": user_email, "read": False}, {"$set": {"read": True}})
        return True
    except Exception as e:
        return False

# ==================== WAREHOUSE STOCK OPERATIONS ====================
def create_warehouse_product(product_name, quantity, price):
    try:
        existing = products.find_one({"name": product_name, "type": "warehouse"})
        if existing:
            return False, "Product already exists in warehouse"
        product_data = {
            "name": product_name,
            "quantity": quantity,
            "price": price,
            "type": "warehouse",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        products.insert_one(product_data)


        movement_data = {
            "product_name": product_name,
            "movement_type": "IN",
            "quantity": quantity,
            "previous_quantity": 0,
            "new_quantity": quantity,
            "notes": "Initial stock added",
            "user_email": "system",
            "timestamp": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        transfers.insert_one(movement_data)

        return True, f"Product '{product_name}' added to warehouse successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_warehouse_products():
    try:
        return list(products.find({"type": "warehouse"}))
    except Exception as e:
        print(f"Error getting warehouse products: {e}")
        return []

def update_warehouse_product(product_name, quantity, price):
    try:
        result = products.update_one(
            {"name": product_name, "type": "warehouse"},
            {"$set": {"quantity": quantity, "price": price, "updated_at": datetime.now()}}
        )
        if result.modified_count > 0:
            return True, "Product updated successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_warehouse_product(product_name):
    try:
        result = products.delete_one({"name": product_name, "type": "warehouse"})
        if result.deleted_count > 0:
            return True, "Product deleted successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_warehouse_products(keyword):
    try:
        return list(products.find({
            "type": "warehouse",
            "name": {"$regex": keyword, "$options": "i"}
        }))
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

# ==================== STOCK MOVEMENT TRACKING ====================
def record_stock_movement(product_name, movement_type, quantity, notes, user_email):
    try:
        product = products.find_one({"name": product_name, "type": "warehouse"})
        if not product:
            return False, "Product not found in warehouse"

        if movement_type == "IN":
            new_quantity = product['quantity'] + quantity
        else:
            if product['quantity'] < quantity:
                return False, f"Insufficient stock. Only {product['quantity']:.2f} KG available"
            new_quantity = product['quantity'] - quantity

        products.update_one(
            {"_id": product['_id']},
            {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
        )

        movement_data = {
            "product_name": product_name,
            "movement_type": movement_type,
            "quantity": quantity,
            "previous_quantity": product['quantity'],
            "new_quantity": new_quantity,
            "notes": notes,
            "user_email": user_email,
            "timestamp": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        transfers.insert_one(movement_data)

        if new_quantity < 10:
            create_alert("low_stock", product_name, new_quantity,
                         f"Low stock: {product_name} has only {new_quantity:.2f} KG")

        movement_text = "added to" if movement_type == "IN" else "removed from"
        return True, f"{quantity:.2f} KG {movement_text} {product_name}. New stock: {new_quantity:.2f} KG"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_movements():
    try:
        return list(transfers.find({}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting all movements: {e}")
        return []

def get_movements_by_type(movement_type):
    try:
        return list(transfers.find({"movement_type": movement_type}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting movements by type: {e}")
        return []

def get_movements_by_date_range(start_date, end_date):
    try:
        return list(transfers.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting movements by date: {e}")
        return []

def get_product_movement_history(product_name):
    try:
        return list(transfers.find({"product_name": product_name}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting product history: {e}")
        return []

def get_low_stock_products():
    try:
        warehouse_products = get_all_warehouse_products()
        return [p for p in warehouse_products if p['quantity'] < 10]
    except Exception as e:
        print(f"Error getting low stock products: {e}")
        return []

# ==================== STOCK REQUEST SYSTEM ====================
def create_stock_request(product_name, quantity, supermarket_email, warehouse_email):
    try:
        request_data = {
            "type": "request",
            "product_name": product_name,
            "quantity": quantity,
            "supermarket_email": supermarket_email,
            "warehouse_email": warehouse_email,
            "message": f"REQUEST from {supermarket_email}: {quantity} KG of {product_name}",
            "timestamp": datetime.now(),
            "read": False,
            "processed": False
        }
        alerts.insert_one(request_data)
        create_notification(warehouse_email, "New Stock Request",
                            f"{supermarket_email} requests {quantity} KG of {product_name}", "request")
        return True, "Request sent"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_pending_requests_for_warehouse(warehouse_email):
    try:
        return list(alerts.find({
            "type": "request",
            "warehouse_email": warehouse_email,
            "processed": False
        }).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting pending requests: {e}")
        return []

def approve_stock_request(request_id, warehouse_email):
    try:
        from bson import ObjectId
        request = alerts.find_one({"_id": ObjectId(request_id), "type": "request", "processed": False})
        if not request:
            return False, "Request not found or already processed"

        product_name = request['product_name']
        quantity = request['quantity']
        supermarket_email = request['supermarket_email']

        warehouse_product = products.find_one({"name": product_name, "type": "warehouse"})
        if not warehouse_product:
            return False, f"Product '{product_name}' not found in warehouse"
        if warehouse_product['quantity'] < quantity:
            return False, f"Insufficient stock. Only {warehouse_product['quantity']:.2f} KG available"

        new_warehouse_qty = warehouse_product['quantity'] - quantity
        products.update_one(
            {"_id": warehouse_product['_id']},
            {"$set": {"quantity": new_warehouse_qty, "updated_at": datetime.now()}}
        )

        movement_data = {
            "product_name": product_name,
            "movement_type": "OUT",
            "quantity": quantity,
            "previous_quantity": warehouse_product['quantity'],
            "new_quantity": new_warehouse_qty,
            "notes": f"Approved request from {supermarket_email}",
            "user_email": warehouse_email,
            "from_email": warehouse_email,
            "to_email": supermarket_email,
            "timestamp": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "completed"
        }
        transfers.insert_one(movement_data)

        supermarket_product = products.find_one({"name": product_name, "type": "supermarket"})
        if supermarket_product:
            new_super_qty = supermarket_product['quantity'] + quantity
            products.update_one(
                {"_id": supermarket_product['_id']},
                {"$set": {
                    "quantity": new_super_qty,
                    "cost_price": warehouse_product['price'],
                    "updated_at": datetime.now()
                }}
            )
        else:
            product_data = {
                "name": product_name,
                "quantity": quantity,
                "cost_price": warehouse_product['price'],
                "selling_price": 0,
                "type": "supermarket",
                "source_warehouse": warehouse_email,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            products.insert_one(product_data)

        alerts.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"processed": True, "read": True,
                      "approved_by": warehouse_email, "approved_at": datetime.now()}}
        )

        create_notification(supermarket_email, "Stock Request Approved",
                            f"Your request for {quantity} KG of {product_name} has been approved and sent", "approved")

        return True, f"Approved and sent {quantity} KG of {product_name} to {supermarket_email}"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== SUPERMARKET OPERATIONS ====================
def receive_stock_from_warehouse(product_name, quantity, cost_price, source_warehouse):
    try:
        existing = products.find_one({"name": product_name, "type": "supermarket"})
        if existing:
            new_quantity = existing['quantity'] + quantity
            products.update_one(
                {"_id": existing['_id']},
                {"$set": {
                    "quantity": new_quantity,
                    "cost_price": cost_price,
                    "source_warehouse": source_warehouse,
                    "updated_at": datetime.now()
                }}
            )
            create_alert("receive", product_name, quantity,
                         f"Received {quantity} KG of {product_name} from warehouse")
        else:
            product_data = {
                "name": product_name,
                "quantity": quantity,
                "cost_price": cost_price,
                "selling_price": 0,
                "type": "supermarket",
                "source_warehouse": source_warehouse,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            products.insert_one(product_data)
            create_alert("new_product", product_name, quantity,
                         f"New product '{product_name}' received from warehouse")
        return True, f"Received {quantity} KG of {product_name} successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_supermarket_products():
    try:
        return list(products.find({"type": "supermarket"}))
    except Exception as e:
        print(f"Error getting supermarket products: {e}")
        return []

def update_selling_price(product_name, selling_price):
    try:
        result = products.update_one(
            {"name": product_name, "type": "supermarket"},
            {"$set": {"selling_price": selling_price, "updated_at": datetime.now()}}
        )
        if result.modified_count > 0:
            return True, f"Selling price for '{product_name}' updated to ${selling_price:.2f} per KG"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def record_sale(product_name, quantity_sold, selling_price):
    try:
        product = products.find_one({"name": product_name, "type": "supermarket"})
        if not product:
            return False, "Product not found in supermarket inventory"
        if product['quantity'] < quantity_sold:
            return False, f"Insufficient stock. Only {product['quantity']:.2f} KG available"

        cost_price = product.get('cost_price', 0)
        revenue = quantity_sold * selling_price
        cost = quantity_sold * cost_price
        profit = revenue - cost

        new_quantity = product['quantity'] - quantity_sold
        products.update_one(
            {"_id": product['_id']},
            {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
        )

        sale_data = {
            "product_name": product_name,
            "quantity_sold": quantity_sold,
            "selling_price": selling_price,
            "cost_price": cost_price,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now()
        }
        sales.insert_one(sale_data)
        return True, f"Sale recorded! Profit: ${profit:,.2f}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_today_sales():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        return list(sales.find({"date": today}))
    except Exception as e:
        print(f"Error getting today's sales: {e}")
        return []

def get_all_sales():
    try:
        return list(sales.find({}))
    except Exception as e:
        print(f"Error getting all sales: {e}")
        return []

def get_today_profit():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = list(sales.find({"date": today}))
        return sum(sale['profit'] for sale in today_sales)
    except Exception as e:
        print(f"Error getting today's profit: {e}")
        return 0

def get_total_profit():
    try:
        all_sales = list(sales.find({}))
        return sum(sale['profit'] for sale in all_sales)
    except Exception as e:
        print(f"Error getting total profit: {e}")
        return 0

def get_total_revenue():
    try:
        all_sales = list(sales.find({}))
        return sum(sale['revenue'] for sale in all_sales)
    except Exception as e:
        print(f"Error getting total revenue: {e}")
        return 0

def get_low_stock_alerts():
    try:
        supermarket_products = get_all_supermarket_products()
        return [p for p in supermarket_products if p['quantity'] < 10]
    except Exception as e:
        print(f"Error getting low stock alerts: {e}")
        return []

# ==================== ALERT OPERATIONS ====================
def create_alert(alert_type, product_name, quantity, message):
    try:
        alert_data = {
            "type": alert_type,
            "product_name": product_name,
            "quantity": quantity,
            "message": message,
            "timestamp": datetime.now(),
            "read": False
        }
        alerts.insert_one(alert_data)
        return True
    except Exception as e:
        print(f"Error creating alert: {e}")
        return False

def get_unread_alerts():
    try:
        return list(alerts.find({"read": False}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting unread alerts: {e}")
        return []

def get_all_alerts():
    try:
        return list(alerts.find({}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting all alerts: {e}")
        return []

def mark_alerts_as_read():
    try:
        alerts.update_many({"read": False}, {"$set": {"read": True}})
        return True
    except Exception as e:
        print(f"Error marking alerts as read: {e}")
        return False

# ==================== TRANSFER OPERATIONS ====================
def create_transfer(from_email, to_email, product_name, quantity):
    transfer_data = {
        "from_email": from_email,
        "to_email": to_email,
        "product_name": product_name,
        "quantity": quantity,
        "timestamp": datetime.now(),
        "status": "completed"
    }
    return transfers.insert_one(transfer_data)

def get_all_transfers():
    try:
        return list(transfers.find({}))
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []

def get_transfers_by_role(role):
    try:
        return list(transfers.find({}))
    except Exception as e:
        print(f"Error getting transfers by role: {e}")
        return []