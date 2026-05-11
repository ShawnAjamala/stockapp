"""
DATABASE MODULE - Handles all MongoDB operations for authentication
"""
from pymongo import MongoClient
from datetime import datetime
import hashlib
import secrets

# ==================== DATABASE CONNECTION ====================
# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")

# Create/Use database called 'supermarket_storage'
db = client.supermarket_storage

# Create users collection
users_collection = db.users

# ==================== PASSWORD HASHING ====================
def hash_password(password):
    """Convert plain text password to a secure hash"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(stored_password, provided_password):
    """Check if entered password matches the stored hash"""
    try:
        salt, hash_value = stored_password.split(':')
        provided_hash = hashlib.sha256((provided_password + salt).encode()).hexdigest()
        return provided_hash == hash_value
    except:
        return False

# ==================== USER MANAGEMENT ====================
def create_default_user():
    """Create default admin user if no users exist"""
    if users_collection.count_documents({}) == 0:
        hashed_password = hash_password("admin123")
        
        admin_user = {
            "email": "admin@supermarket.com",
            "password": hashed_password,
            "fullname": "System Administrator",
            "role": "admin",
            "created_at": datetime.now()
        }
        
        result = users_collection.insert_one(admin_user)
        print(f"✓ Default admin user created")
        print("  Email: admin@supermarket.com")
        print("  Password: admin123")
        return result.inserted_id
    return None

def verify_user(email, password):
    """Verify user credentials during login using email"""
    user = users_collection.find_one({"email": email})
    if user:
        if verify_password(user["password"], password):
            return True
    return False

def register_user(email, password, fullname=""):
    """Register a new user using email as unique identifier"""
    try:
        # Check if email exists
        if users_collection.find_one({"email": email}):
            return False, "Email already registered! Please use another email."
        
        hashed_password = hash_password(password)
        
        new_user = {
            "email": email,
            "password": hashed_password,
            "fullname": fullname,
            "role": "user",
            "created_at": datetime.now()
        }
        
        result = users_collection.insert_one(new_user)
        return True, f"Account created successfully with email: {email}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_info(email):
    """Get user information (without password)"""
    user = users_collection.find_one({"email": email})
    if user:
        return {
            "email": user["email"],
            "fullname": user.get("fullname", ""),
            "role": user.get("role", "user"),
            "created_at": user["created_at"]
        }
    return None

# Create default user when module loads
create_default_user()