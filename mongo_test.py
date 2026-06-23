from pymongo import MongoClient

MONGO_URI = "YOUR_CONNECTION_STRING"

client = MongoClient(MONGO_URI)

print("Connected Successfully")

print(client.list_database_names())