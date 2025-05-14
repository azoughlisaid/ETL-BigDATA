from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
collection = db["user_activity_processed"]

count = collection.count_documents({})
print(f"📦 Nombre de documents dans la collection : {count}")

# Afficher les 3 premiers documents
for doc in collection.find().limit(3):
    print(doc)
