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

# Allows the database to track products inserted by the user
def create_product(user_email, product_name, quantity, price):
    """Insert new product for a user"""
    product_data = {
        "user_email": user_email,
        "name": product_name,
        "quantity": quantity,
        "price": price,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return products.insert_one(product_data)

def get_products_by_user(user_email):
    """Get all products for a specific user"""
    return list(products.find({"user_email": user_email}))

def get_all_products():
    """Get all products from all users"""
    return list(products.find({}))

def update_product_quantity(product_id, new_quantity):
    """Update product quantity by product ID"""
    return products.update_one(
        {"_id": product_id},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
    )

def delete_product(product_id):
    """Delete product by ID"""
    return products.delete_one({"_id": product_id})

def find_product_by_name_and_user(product_name, user_email):
    """Find product by name and user email"""
    return products.find_one({"name": product_name, "user_email": user_email})

# Allows data to be transfered between users for easy management of warehouse and supermarket stock data
def create_transfer(from_email, to_email, product_name, quantity):
    """Record a transfer between users"""
    transfer_data = {
        "from_email": from_email,
        "to_email": to_email,
        "product_name": product_name,
        "quantity": quantity,
        "timestamp": datetime.now(),
        "status": "completed"
    }
    return transfers.insert_one(transfer_data)

def get_transfers_by_user(email):
    """Get all transfers where user is sender or receiver"""
    return list(transfers.find({
        "$or": [
            {"from_email": email},
            {"to_email": email}
        ]
    }))

def get_all_transfers():
    """Get all transfers"""
    return list(transfers.find({}))