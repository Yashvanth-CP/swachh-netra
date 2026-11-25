import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
url = os.getenv("MONGO_URL")
print("URL found:", url is not None)

client = MongoClient(url, serverSelectionTimeoutMS=5000)
print(client.admin.command("ping"))
print("Connected to MongoDB!")