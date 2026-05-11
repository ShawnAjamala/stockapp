"""
DATABASE MODULE - Handles all MongoDB operations for authentication
"""
from pymongo import MongoClient
from datetime import datetime
import hashlib
import secrets

# ==================== DATABASE CONNECTION ====================
# Connect to MongoDB Atlas (your cloud database)
client = MongoClient("mongodb+srv://shawnajamala1_db_user:LlLBJrjkXIyn5bGh@cluster0.yqqbhoe.mongodb.net/?appName=Cluster0")

# Create/Use database called 'supermarket_storage'
db = client.supermarket_storage

# Create users collection (like a table for user accounts)
users_collection = db.users

# ==================== PASSWORD HASHING ====================
def hash_password(password):
    """
    Convert plain text password to a secure hash
    Uses SHA-256 + random salt (no extra libraries needed)
    """
    # Generate a random salt (16 bytes = 32 hex characters)
    salt = secrets.token_hex(16)
    
    # Combine password with salt and hash it
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Store salt and hash together (separated by colon)
    return f"{salt}:{password_hash}"

def verify_password(stored_password, provided_password):
    """
    Check if entered password matches the stored hash
    """
    try:
        # Split the stored value into salt and hash
        salt, hash_value = stored_password.split(':')
        
        # Hash the provided password with the same salt
        provided_hash = hashlib.sha256((provided_password + salt).encode()).hexdigest()
        
        # Compare hashes
        return provided_hash == hash_value
    except:
        return False

# ==================== USER MANAGEMENT ====================
def create_default_user():
    """
    Create default admin user if no users exist in database
    This runs automatically when the app starts
    """
    # Check if users collection is empty
    if users_collection.count_documents({}) == 0:
        # Hash the default password
        hashed_password = hash_password("admin123")
        
        # Create admin user document
        admin_user = {
            "username": "admin",
            "password": hashed_password,
            "fullname": "System Administrator",
            "role": "admin",
            "created_at": datetime.now()
        }
        
        # Insert into database
        result = users_collection.insert_one(admin_user)
        print(f"✓ Default admin user created with ID: {result.inserted_id}")
        print("  Username: admin")
        print("  Password: admin123")
        return result.inserted_id
    return None

def verify_user(username, password):
    """
    Verify user credentials during login
    Returns True if valid, False otherwise
    """
    # Find user by username
    user = users_collection.find_one({"username": username})
    
    if user:
        # Check if password matches
        if verify_password(user["password"], password):
            return True
    
    return False

def register_user(username, password, fullname=""):
    """
    Register a new user
    Returns: (success boolean, message string)
    """
    try:
        # Check if username already exists
        if users_collection.find_one({"username": username}):
            return False, "Username already exists! Please choose another."
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Create new user document
        new_user = {
            "username": username,
            "password": hashed_password,
            "fullname": fullname,
            "role": "user",
            "created_at": datetime.now()
        }
        
        # Insert into database
        result = users_collection.insert_one(new_user)
        print(f"✓ New user created: {username} (ID: {result.inserted_id})")
        
        return True, f"User '{username}' created successfully!"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_info(username):
    """
    Get user information (without password)
    """
    user = users_collection.find_one({"username": username})
    if user:
        return {
            "username": user["username"],
            "fullname": user.get("fullname", ""),
            "role": user.get("role", "user"),
            "created_at": user["created_at"]
        }
    return None

# ==================== TEST CONNECTION ====================
if __name__ == "__main__":
    print("=" * 50)
    print("TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    # Test connection
    try:
        client.admin.command('ping')
        print("✓ Connected to MongoDB Atlas successfully!")
        print(f"✓ Using database: {db.name}")
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
    
    # Create default user
    create_default_user()
    
    # List all users
    print("\n" + "=" * 50)
    print("REGISTERED USERS")
    print("=" * 50)
    all_users = users_collection.find({})
    for user in all_users:
        print(f"  • {user['username']} - {user.get('fullname', 'No name')} - Role: {user.get('role', 'user')}")
    
    # Test login
    print("\n" + "=" * 50)
    print("TESTING LOGIN")
    print("=" * 50)
    
    # Test with correct password
    if verify_user("admin", "admin123"):
        print("✓ Login successful with admin/admin123")
    else:
        print("✗ Login failed")
    
    # Test with wrong password
    if verify_user("admin", "wrongpassword"):
        print("✓ Login successful with wrong password (ERROR!)")
    else:
        print("✓ Wrong password correctly rejected")