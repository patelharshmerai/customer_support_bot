# src/db/queue_db.py

from pymongo.errors import DuplicateKeyError
from src.config.db_config import get_database

db = get_database()
queue_collection = db["queue"]

# Ensure phone number is unique in the queue
queue_collection.create_index("phone", unique=True)

def add_to_queue(name: str, phone: str) -> bool:
    """
    Adds a user to the call queue if not already scheduled.
    Returns True if added, False if already exists.
    """
    doc = {
        "name": name,
        "phone": phone
    }
    try:
        queue_collection.insert_one(doc)
        return True
    except DuplicateKeyError:
        return False
