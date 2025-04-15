# setup_mongo.py

from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create or access the 'merilBot' database
db = client["merilBot"]

# Create or access the 'users' collection
users_collection = db["users"]

# Ensure 'phone' is unique
users_collection.create_index("phone", unique=True)

# Insert a test user (optional)
sample_user = {
    "phone": "9999999999",
    "name": "Test User",
    "purchase_history": [],
    "chat_history": []
}

# Insert only if not already present
if not users_collection.find_one({"phone": sample_user["phone"]}):
    users_collection.insert_one(sample_user)
    print("Sample user inserted.")
else:
    print("Sample user already exists.")

# Verify
print("Connected to DB. Users count:", users_collection.count_documents({}))
