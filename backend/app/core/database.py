import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME", "swachh_netra")]

complaints_col = db["complaints"]   # a "collection" = like a table
users_col = db["users"]
users_col.create_index("email", unique=True)   # no duplicate emails