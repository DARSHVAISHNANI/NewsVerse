# db_manager.py

from pymongo import MongoClient
from typing import List, Dict

# Import our settings from the config file
from Sentiment_Analysis import config

def ConnectToMongoDB():
    """
    Establishes a connection to MongoDB and returns the collection object.
    """
    try:
        client = MongoClient(config.MONGO_URI)
        db = client[config.DB_NAME]
        collection = db[config.COLLECTION_NAME]
        print("✅ Successfully connected to MongoDB.")
        return collection
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def FetchArticlesToAnalyzeSentiment(collection) -> List[Dict]:
    """
    Fetches all articles that are missing a sentiment.
    """
    if collection is None:
        return []

    articles = list(collection.find({
        "$or": [
            {"sentiment": {"$exists": False}}
        ]
    }))
    print(f"🔍 Found {len(articles)} articles with missing sentiment.")
    return articles

def UpdateArticleSentiment(collection, article_id, sentiment_label: str):
    """
    Updates a single article with the sentiment.
    """
    if collection is None:
        return

    collection.update_one(
        {"_id": article_id},
        {"$set": {
            "sentiment": sentiment_label
        }}
    )