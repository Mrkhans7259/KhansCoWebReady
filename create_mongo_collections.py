from pymongo import MongoClient

MONGO_URI = "YOUR_MONGODB_ATLAS_CONNECTION_STRING"

client = MongoClient(MONGO_URI)

db = client["khansco"]

collections = [
    "clients",
    "users",
    "fees",
    "gst_status",
    "invoices",
    "tickets",
    "documents",
    "notifications",
    "client_files",
    "work_progress",
    "client_logins"
]

for collection in collections:
    if collection not in db.list_collection_names():
        db.create_collection(collection)
        print(f"Created: {collection}")
    else:
        print(f"Already exists: {collection}")

print("\nCollections in khansco database:")
print(db.list_collection_names())