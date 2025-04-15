# File: src/db/user_db.py
from src.config.db_config import get_database

db = get_database()
user_collection = db["users"]
# Ensure 'phone' is a unique key
user_collection.create_index("phone", unique=True)

def create_user(name: str, phone: str) -> bool:
    """
    Creates a new user in the DB.
    Returns True if creation was successful, False if user already exists.
    """
    # Basic structure for each user
    user_doc = {
        "phone": phone,
        "name": name,
        "purchase_history": [],
        "chat_history": []  # we’ll store raw conversation logs here
    }
    try:
        user_collection.insert_one(user_doc)
        return True
    except Exception as e:
        # If phone already exists or insertion fails
        print(f"create_user error: {e}")
        return False

def get_user_by_phone(phone: str) -> dict:
    """
    Retrieves a user by phone number.
    Returns the user document or None if not found.
    """
    return user_collection.find_one({"phone": phone})

def update_user_chat(phone: str, message: str, sender: str = "user"):
    """
    Appends a new message to the user's chat history (simple example).
    """
    user_collection.update_one(
        {"phone": phone},
        {"$push": {"chat_history": f"{sender}: {message}"}}
    )
