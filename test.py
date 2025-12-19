from pymongo import MongoClient
import urllib.parse
from pymongo.server_api import ServerApi

username = urllib.parse.quote_plus("Datasets")
password = urllib.parse.quote_plus("Datasets123")

uri = (
    f"mongodb+srv://{username}:{password}"
    "@cluster1.r2hvgus.mongodb.net/"
    "?authSource=admin&retryWrites=true&w=majority"
)

client = MongoClient(uri, server_api=ServerApi('1'))

# Pick (or create) a database
db = client["Datasets_test"]

# Pick (or create) a collection
collection = db["devices"]

def data_input():
    data = {
        "name": "Alice",
        "age": 25,
        "skills": ["python", "mongodb"],
        "active": True
    }
    
    result = collection.insert_one(data)
    return result.inserted_id