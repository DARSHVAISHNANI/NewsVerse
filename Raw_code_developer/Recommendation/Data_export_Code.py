import json
import certifi
from pymongo import MongoClient

# -----------------------------
# MongoDB Atlas Connection
# -----------------------------
MONGO_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/" 
DB_NAME = "NewsVerseDB"
COLLECTION_NAME = "NewsVerseCo"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
collection = client[DB_NAME][COLLECTION_NAME]

# -----------------------------
# Export Collection to JSON
# -----------------------------
output_file = "mongo_export.json"

# Fetch all documents
docs = list(collection.find({}))

# Convert ObjectId to string for JSON serialization
for doc in docs:
    doc["_id"] = str(doc["_id"])

# Save to JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=4, ensure_ascii=False)

print(f"✅ Exported {len(docs)} documents to {output_file}")