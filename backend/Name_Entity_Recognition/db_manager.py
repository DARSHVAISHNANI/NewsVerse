# in ner_processor/db_manager.py

import certifi
from pymongo import MongoClient
# This is no longer needed here as we are not converting to ObjectId
# from bson import ObjectId 

# Import our settings from the config file
from Name_Entity_Recognition import config

def connectToDbs():
    """
    Connects to MongoDB and returns the news and user collection objects.
    Returns a tuple: (news_collection, user_collection)
    """
    try:
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
        news_db = client[config.NEWS_DB_NAME]
        news_collection = news_db[config.NEWS_COLLECTION_NAME]
        user_db = client[config.USER_DB_NAME]
        user_collection = user_db[config.USER_COLLECTION_NAME]
        print("✅ Successfully connected to both News and User DB collections.")
        return news_collection, user_collection
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None, None

def fetchAllUsers(user_collection):
    """Fetches all users from the user collection."""
    if user_collection is None:
        return []
    return list(user_collection.find({}))

def fetchArticleById(news_collection, article_id):
    """Fetches a single article by its string ID."""
    if news_collection is None:
        return None
    try:
        # UPDATED: Removed the ObjectId() conversion to search by the actual string ID
        return news_collection.find_one({"_id": article_id})
    except Exception as e:
        # This catch block might not be necessary anymore but is safe to keep
        print(f"❗ An error occurred fetching article {article_id}: {e}")
        return None

def updateUserNer(user_collection, user_mongo_id, ner_data):
    """Updates a user document with the aggregated NER data."""
    if user_collection is None:
        return

    user_collection.update_one(
        {"_id": user_mongo_id},
        {"$set": {"ner_data": ner_data}}
    )