# in ner_processor/db_manager.py

import certifi
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

# Import our settings from the config file
from Name_Entity_Recognition import config

logger = logging.getLogger("NERPipeline.db_manager")

def connectToDbs():
    """
    Connects to MongoDB and returns the news and user collection objects.
    Returns a tuple: (news_collection, user_collection)
    """
    try:
        if not config.MONGO_URI:
            logger.error("❌ MONGO_URI is not set in config. Cannot connect to database.")
            return None, None
            
        logger.info(f"Attempting to connect to MongoDB at: {config.MONGO_URI[:20]}...")
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        news_db = client[config.NEWS_DB_NAME]
        news_collection = news_db[config.NEWS_COLLECTION_NAME]
        user_db = client[config.USER_DB_NAME]
        user_collection = user_db[config.USER_COLLECTION_NAME]
        
        # Verify collections exist and are accessible
        news_count = news_collection.count_documents({}, limit=1)
        user_count = user_collection.count_documents({}, limit=1)
        
        logger.info(f"✅ Successfully connected to both News and User DB collections.")
        logger.info(f"   News collection '{config.NEWS_COLLECTION_NAME}' has documents: {news_count >= 0}")
        logger.info(f"   User collection '{config.USER_COLLECTION_NAME}' has documents: {user_count >= 0}")
        return news_collection, user_collection
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ Failed to connect to MongoDB (connection/timeout error): {e}")
        return None, None
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}", exc_info=True)
        return None, None

def fetchAllUsers(user_collection):
    """Fetches all users from the user collection."""
    if user_collection is None:
        logger.warning("❌ User collection is None. Cannot fetch users.")
        return []
    try:
        users = list(user_collection.find({}))
        logger.info(f"✅ Fetched {len(users)} users from database")
        return users
    except Exception as e:
        logger.error(f"❌ Error fetching users from database: {e}", exc_info=True)
        return []

def fetchArticleById(news_collection, article_id):
    """Fetches a single article by its string ID."""
    if news_collection is None:
        logger.warning("❌ News collection is None. Cannot fetch article.")
        return None
    
    # If the article_id is None or an empty string, skip it.
    if not article_id:
        logger.debug(f"❗ Received empty or None article_id, skipping.")
        return None
    
    try:
        # Try exact string match first (most common case)
        article = news_collection.find_one({"_id": article_id})
        
        if article is None:
            # Try as ObjectId if the string looks like an ObjectId
            try:
                from bson import ObjectId
                if len(article_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in article_id):
                    article = news_collection.find_one({"_id": ObjectId(article_id)})
            except Exception:
                pass
            
            if article is None:
                logger.warning(f"   ⚠️ Article '{article_id}' not found in database")
                # Debug: Check if similar IDs exist (first few chars match)
                if len(article_id) > 5:
                    prefix = article_id[:10]
                    similar = list(news_collection.find({"_id": {"$regex": f"^{prefix}"}}, {"_id": 1}).limit(5))
                    if similar:
                        logger.debug(f"   Found similar IDs starting with '{prefix}': {[doc['_id'] for doc in similar]}")
        else:
            logger.debug(f"   ✅ Found article '{article_id}'")
            
        return article
    except Exception as e:
        # Catch any other unexpected database errors
        logger.error(f"   ❌ An unexpected error occurred fetching article {article_id}: {e}", exc_info=True)
        return None

def updateUserNer(user_collection, user_mongo_id, ner_data):
    """Updates a user document with the aggregated NER data."""
    if user_collection is None:
        logger.error("❌ User collection is None. Cannot update NER data.")
        return False

    try:
        result = user_collection.update_one(
            {"_id": user_mongo_id},
            {"$set": {"ner_data": ner_data}}
        )
        
        if result.matched_count == 0:
            logger.warning(f"❗ No user found with _id: {user_mongo_id}")
            return False
        elif result.modified_count == 0:
            logger.warning(f"❗ User {user_mongo_id} found but NER data was not modified (might be identical)")
            return True  # Still return True as the operation succeeded
        else:
            logger.info(f"✅ Successfully updated NER data for user {user_mongo_id}")
            return True
    except OperationFailure as e:
        logger.error(f"❌ MongoDB operation failed while updating NER data for user {user_mongo_id}: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error updating NER data for user {user_mongo_id}: {e}", exc_info=True)
        return False