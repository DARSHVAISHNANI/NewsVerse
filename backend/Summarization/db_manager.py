# db_manager.py

from pymongo import MongoClient
from typing import List, Dict

# Import our settings from the config file
from Summarization import config

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

def FetchArticlesToSummarize(collection) -> List[Dict]:
    """
    Fetches all articles that are missing a summary or a story summary.
    """
    if collection is None:
        return []

    articles = list(collection.find({
        "$or": [
            {"summarization": {"$exists": False}},
            {"summarization.summary": {"$in": [None, ""]}},
            {"summarization.story_summary": {"$in": [None, ""]}}
        ]
    }))
    print(f"🔍 Found {len(articles)} articles to summarize.")
    return articles

def UpdateArticleSummaries(collection, article_id, summary_text: str, story_text: str):
    """
    Updates a single article with the new factual and story summaries.
    """
    if collection is None:
        return

    collection.update_one(
        {"_id": article_id},
        {"$set": {
            "summarization": {
                "summary": summary_text,
                "story_summary": story_text
            }
        }}
    )