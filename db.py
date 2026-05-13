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
sales = db.sales  # New collection for sales records
alerts = db.alerts  # New collection for alerts

# Fixed role passwords
SUPERMARKET_PASSWORD = "000000"
WAREHOUSE_PASSWORD = "111111"

def hash_password(password):
    # Hash password using SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

# Checks for users within the database
def create_user(email, password, fullname, role):
    # Insert new user into database
    user_data = {
        "email": email,
        "password": hash_password(password),
        "fullname": fullname,
        "role": role,
        "created_at": datetime.now()
    }
    return users.insert_one(user_data)

def find_user_by_email(email):
    # Find user by email
    return users.find_one({"email": email})

def find_user_by_email_and_password(email, password):
    # Find user by email and password
    return users.find_one({"email": email, "password": hash_password(password)})

def get_all_users():
    # Get all users
    return list(users.find({}))

def get_users_by_role(role):
    # Get users by role
    return list(users.find({"role": role}))

# ==================== WAREHOUSE STOCK OPERATIONS ====================
# All warehouse admins share the same data

def create_warehouse_product(product_name, quantity, price):
    # Insert new product for warehouse - ALL warehouse admins can see
    try:
        # Check if product already exists in warehouse
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
        return True, f"Product '{product_name}' added to warehouse successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_warehouse_products():
    # Get ALL warehouse products - visible to every warehouse admin
    try:
        return list(products.find({"type": "warehouse"}))
    except Exception as e:
        print(f"Error getting warehouse products: {e}")
        return []

def update_warehouse_product(product_name, quantity, price):
    # Update warehouse product by name - affects all warehouse admins
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
    # Delete warehouse product by name - removes for all warehouse admins
    try:
        result = products.delete_one({"name": product_name, "type": "warehouse"})
        if result.deleted_count > 0:
            return True, "Product deleted successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_warehouse_products(keyword):
    # Search warehouse products by name - across all warehouse data
    try:
        return list(products.find({
            "type": "warehouse",
            "name": {"$regex": keyword, "$options": "i"}
        }))
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

# ==================== SUPERMARKET RECEIVE AND SALES OPERATIONS ====================

def receive_stock_from_warehouse(product_name, quantity, cost_price, source_warehouse):
    # Receive stock from warehouse to supermarket
    # Adds to supermarket inventory with cost price
    try:
        # Check if product already exists in supermarket
        existing = products.find_one({"name": product_name, "type": "supermarket"})
        
        if existing:
            # Update existing product - add to quantity, update cost price
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
            # Create alert for received stock
            create_alert("receive", product_name, quantity, f"Received {quantity} KG of {product_name} from warehouse")
        else:
            # Create new product in supermarket
            product_data = {
                "name": product_name,
                "quantity": quantity,
                "cost_price": cost_price,
                "selling_price": 0,  # To be set by supermarket admin
                "type": "supermarket",
                "source_warehouse": source_warehouse,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            products.insert_one(product_data)
            # Create alert for new product received
            create_alert("new_product", product_name, quantity, f"New product '{product_name}' received from warehouse")
        
        return True, f"Received {quantity} KG of {product_name} successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_supermarket_products():
    # Get ALL supermarket products - visible to every supermarket admin
    try:
        return list(products.find({"type": "supermarket"}))
    except Exception as e:
        print(f"Error getting supermarket products: {e}")
        return []

def update_selling_price(product_name, selling_price):
    # Update the selling price per KG for a supermarket product
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
    # Record a sale of a product
    # Deducts from supermarket stock and records profit
    try:
        # Get current supermarket product
        product = products.find_one({"name": product_name, "type": "supermarket"})
        
        if not product:
            return False, "Product not found in supermarket inventory"
        
        if product['quantity'] < quantity_sold:
            return False, f"Insufficient stock. Only {product['quantity']:.2f} KG available"
        
        # Get cost price (original price from warehouse)
        cost_price = product.get('cost_price', 0)
        
        # Calculate revenue and profit
        revenue = quantity_sold * selling_price
        cost = quantity_sold * cost_price
        profit = revenue - cost
        
        # Update supermarket stock
        new_quantity = product['quantity'] - quantity_sold
        products.update_one(
            {"_id": product['_id']},
            {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
        )
        
        # Record the sale in sales collection
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
    # Get all sales for today
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        return list(sales.find({"date": today}))
    except Exception as e:
        print(f"Error getting today's sales: {e}")
        return []

def get_all_sales():
    # Get all sales history
    try:
        return list(sales.find({}))
    except Exception as e:
        print(f"Error getting all sales: {e}")
        return []

def get_today_profit():
    # Calculate total profit for today
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = list(sales.find({"date": today}))
        total_profit = sum(sale['profit'] for sale in today_sales)
        return total_profit
    except Exception as e:
        print(f"Error getting today's profit: {e}")
        return 0

def get_total_profit():
    # Calculate total profit from all sales
    try:
        all_sales = list(sales.find({}))
        total_profit = sum(sale['profit'] for sale in all_sales)
        return total_profit
    except Exception as e:
        print(f"Error getting total profit: {e}")
        return 0

def get_total_revenue():
    # Calculate total revenue from all sales
    try:
        all_sales = list(sales.find({}))
        total_revenue = sum(sale['revenue'] for sale in all_sales)
        return total_revenue
    except Exception as e:
        print(f"Error getting total revenue: {e}")
        return 0

def get_low_stock_alerts():
    # Get products with low stock (less than 10 KG)
    try:
        supermarket_products = get_all_supermarket_products()
        low_stock = [p for p in supermarket_products if p['quantity'] < 10]
        return low_stock
    except Exception as e:
        print(f"Error getting low stock alerts: {e}")
        return []

# ==================== ALERT OPERATIONS ====================

def create_alert(alert_type, product_name, quantity, message):
    # Create a new alert for the dashboard
    try:
        alert_data = {
            "type": alert_type,  # "receive", "new_product", "low_stock", "sale"
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
    # Get all unread alerts
    try:
        return list(alerts.find({"read": False}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting unread alerts: {e}")
        return []

def mark_alerts_as_read():
    # Mark all alerts as read
    try:
        alerts.update_many({"read": False}, {"$set": {"read": True}})
        return True
    except Exception as e:
        print(f"Error marking alerts as read: {e}")
        return False

def get_all_alerts():
    # Get all alerts
    try:
        return list(alerts.find({}).sort("timestamp", -1))
    except Exception as e:
        print(f"Error getting all alerts: {e}")
        return []

# ==================== TRANSFER OPERATIONS ====================

def create_transfer(from_email, to_email, product_name, quantity):
    # Record a transfer between warehouse and supermarket
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
    # Get all transfers - visible to all admins
    try:
        return list(transfers.find({}))
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []

def get_transfers_by_role(role):
    # Get transfers based on role
    try:
        if role == "warehouse":
            # Warehouse sees transfers they sent
            return list(transfers.find({}))
        else:
            # Supermarket sees all transfers to them
            return list(transfers.find({}))
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []