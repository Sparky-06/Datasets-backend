# from pymongo import MongoClient
# import urllib.parse
# from pymongo.server_api import ServerApi

# username = urllib.parse.quote_plus("Datasets")
# password = urllib.parse.quote_plus("Datasets123")

# uri = (
#     f"mongodb+srv://{username}:{password}"
#     "@cluster1.r2hvgus.mongodb.net/"
#     "?authSource=admin&retryWrites=true&w=majority"
# )

# client = MongoClient(uri, server_api=ServerApi('1'))

# # Pick (or create) a database
# db = client["Datasets_test"]

# # Pick (or create) a collection
# collection = db["devices"]

# def data_input():
#     data = {
#         "name": "Alice",
#         "age": 25,
#         "skills": ["python", "mongodb"],
#         "active": True
#     }
    
#     result = collection.insert_one(data)
#     return result.inserted_id

import requests


EXTERNAL_API_URL = "https://smart-home-agent.onrender.com/automated_events"

def fetch_decision():
        response = requests.get(EXTERNAL_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        light_json = data.get("light_1")
        fan_json   = data.get("fan_1")
        ac_json    = data.get("ac_1")

        print("Light_1:", light_json)
        print("Fan_1:", fan_json)
        print("AC_1:", ac_json)

print(fetch_decision())