import os
import bcrypt
from pymongo import MongoClient
from urllib.parse import quote_plus

def connect_to_cloud_db():
    uri = "MONGODB_URI"  # Load URI securely from environment
    if not uri:
        raise ValueError("MONGODB_URI not set in environment")
    client = MongoClient(uri)
    db = client["cluster_name"]
    users_col = db["users"]
    sessions_col = db["sessions"]
    return users_col, sessions_col

def sign_up(users_col, username, password):
    # Check if user already exists
    if users_col.find_one({"username": username}):
        return False

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_col.insert_one({
        "username": username,
        "pw_hash": pw_hash,
        "session_data": []  # Optional placeholder for future session tracking
    })

    return True

def sign_in(users_col, username, password):
    user = users_col.find_one({"username": username})
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user["pw_hash"])

def delete_account(users_col, sessions_col, username):
    # Delete user credentials
    users_col.delete_one({"username": username})

    # Delete user session data
    sessions_col.delete_many({"username": username})