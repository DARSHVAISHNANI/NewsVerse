# db_manager.py

import certifi
from pymongo import MongoClient

# Import our settings from the config file
from Fact_Checker import config

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

def updateArticleFactCheck(collection, article_id, new_fact_check_data, existing_article):
    """Updates an article with new fact-check data, merging with existing data."""
    if collection is None:
        return

    # Merge new fact check with existing one to preserve other fields (like user_verdict)
    existing_fact_check = existing_article.get("fact_check", {})
    merged_fact_check = {**existing_fact_check, **new_fact_check_data}

    collection.update_one(
        {"_id": article_id},
        {"$set": {"fact_check": merged_fact_check}}
    )