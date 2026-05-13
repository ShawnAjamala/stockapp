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

# Fixed role passwords
SUPERMARKET_PASSWORD = "000000"
WAREHOUSE_PASSWORD = "111111"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Checks for users within the database
def create_user(email, password, fullname, role):
    """Insert new user into database"""
    user_data = {
        "email": email,
        "password": hash_password(password),
        "fullname": fullname,
        "role": role,
        "created_at": datetime.now()
    }
    return users.insert_one(user_data)

def find_user_by_email(email):
    """Find user by email"""
    return users.find_one({"email": email})

def find_user_by_email_and_password(email, password):
    """Find user by email and password"""
    return users.find_one({"email": email, "password": hash_password(password)})

def get_all_users():
    """Get all users"""
    return list(users.find({}))

def get_users_by_role(role):
    """Get users by role"""
    return list(users.find({"role": role}))

# ==================== WAREHOUSE STOCK OPERATIONS (All warehouse admins share data) ====================

def create_warehouse_product(product_name, quantity, price):
    """Insert new product for warehouse - ALL warehouse admins can see"""
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
    """Get ALL warehouse products - visible to every warehouse admin"""
    try:
        return list(products.find({"type": "warehouse"}))
    except Exception as e:
        print(f"Error getting warehouse products: {e}")
        return []

def update_warehouse_product(product_name, quantity, price):
    """Update warehouse product by name - affects all warehouse admins"""
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
    """Delete warehouse product by name - removes for all warehouse admins"""
    try:
        result = products.delete_one({"name": product_name, "type": "warehouse"})
        if result.deleted_count > 0:
            return True, "Product deleted successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_warehouse_products(keyword):
    """Search warehouse products by name - across all warehouse data"""
    try:
        return list(products.find({
            "type": "warehouse",
            "name": {"$regex": keyword, "$options": "i"}
        }))
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

# ==================== SUPERMARKET PRODUCT OPERATIONS (All supermarket admins share data) ====================

def create_supermarket_product(product_name, quantity, price):
    """Insert new product for supermarket - ALL supermarket admins can see"""
    try:
        # Check if product already exists in supermarket
        existing = products.find_one({"name": product_name, "type": "supermarket"})
        if existing:
            return False, "Product already exists in supermarket inventory"
        
        product_data = {
            "name": product_name,
            "quantity": quantity,
            "price": price,
            "type": "supermarket",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        products.insert_one(product_data)
        return True, f"Product '{product_name}' added to supermarket successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_supermarket_products():
    """Get ALL supermarket products - visible to every supermarket admin"""
    try:
        return list(products.find({"type": "supermarket"}))
    except Exception as e:
        print(f"Error getting supermarket products: {e}")
        return []

def update_supermarket_product(product_name, quantity, price):
    """Update supermarket product by name - affects all supermarket admins"""
    try:
        result = products.update_one(
            {"name": product_name, "type": "supermarket"},
            {"$set": {"quantity": quantity, "price": price, "updated_at": datetime.now()}}
        )
        if result.modified_count > 0:
            return True, "Product updated successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_supermarket_product(product_name):
    """Delete supermarket product by name - removes for all supermarket admins"""
    try:
        result = products.delete_one({"name": product_name, "type": "supermarket"})
        if result.deleted_count > 0:
            return True, "Product deleted successfully"
        return False, "Product not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_supermarket_products(keyword):
    """Search supermarket products by name - across all supermarket data"""
    try:
        return list(products.find({
            "type": "supermarket",
            "name": {"$regex": keyword, "$options": "i"}
        }))
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

# ==================== TRANSFER OPERATIONS ====================

def create_transfer(from_email, to_email, product_name, quantity):
    """Record a transfer between warehouse and supermarket"""
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
    """Get all transfers - visible to all admins"""
    try:
        return list(transfers.find({}))
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []

def get_transfers_by_role(role):
    """Get transfers based on role"""
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

