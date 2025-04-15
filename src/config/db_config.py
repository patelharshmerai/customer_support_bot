# File: src/config/db_config.py
import pymongo
from pymongo.errors import ConnectionFailure

def get_database():
    """
    Returns a handle to the 'merilBot' database (or creates it if not found).
    Adjust 'MONGODB_URI' as needed.
    """
    # Example local connection string; replace with your actual MongoDB URI
    MONGODB_URI = "mongodb://localhost:27017/"
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
    except ConnectionFailure:
        print("Server not available")
        raise

    db = client["merilBot"]  
    return db
