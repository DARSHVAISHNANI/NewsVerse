# in article_scorer/db_manager.py

import certifi
from pymongo import MongoClient

# Import our settings from the config file
from Article_Scorer import config

def connectToDb():
    """Connects to MongoDB and returns the collection object."""
    try:
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
        db = client[config.DB_NAME]
        collection = db[config.COLLECTION_NAME]
        print(f"✅ Connected to DB: {db.name}, collection: {collection.name}")
        return collection
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def fetchAllArticles(collection):
    """Fetches all articles from the collection."""
    if collection is None:
        return []

    articles = list(collection.find({}))
    print(f"📦 Found {len(articles)} articles in DB.")
    return articles

def updateArticleScores(collection, doc_id, score_data):
    """Updates a single article with the new score data."""
    if collection is None:
        return

    collection.update_one(
        {"_id": doc_id},
        {"$set": {"article_score": score_data}}
    )