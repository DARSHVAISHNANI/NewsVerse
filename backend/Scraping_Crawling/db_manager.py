# db_manager.py

import json
import os
import random
from datetime import datetime
from typing import List, Dict, Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Import our settings from the config file
import config

# =============================================================================
# MONGODB FUNCTIONS
# =============================================================================

def ConnectToMongoDB() -> Optional[MongoClient]:
    """
    Establish connection to MongoDB Atlas.

    Returns:
        MongoClient instance if successful, None otherwise
    """
    try:
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error connecting to MongoDB: {e}")
        return None


# This is the NEW version for db_manager.py
# Replace the old save_to_mongodb function with this one.

def SaveToMongoDB(articles: List[Dict]) -> bool:
    """
    Save only new articles to MongoDB to avoid duplicates.
    Checks for existing articles based on their URL.
    """
    if not articles:
        print("⚠️  No articles to save to MongoDB.")
        return False

    client = ConnectToMongoDB()
    if not client:
        return False
    
    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]
        
        # 1. Get all the URLs from the articles we just scraped.
        incoming_urls = {article['url'] for article in articles}
        
        # 2. Find which of these URLs already exist in our database.
        # We only need the 'url' field to check for existence.
        existing_urls = {
            doc['url'] for doc in collection.find(
                {'url': {'$in': list(incoming_urls)}},
                {'_id': 0, 'url': 1}
            )
        }
        
        # 3. Figure out which articles are completely new.
        new_articles = [
            article for article in articles if article['url'] not in existing_urls
        ]

        # 4. If there are new articles, add timestamps and insert them.
        if new_articles:
            current_time = datetime.now()
            for article in new_articles:
                article['scraped_at'] = current_time
                # We can simplify the _id generation or keep it as is
                article['_id'] = f"{article['source']}_{current_time.strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            result = collection.insert_many(new_articles)
            print(f"✅ Found {len(new_articles)} new articles. Saved them to MongoDB.")
            return True
        else:
            print("✅ No new articles found. Database is already up-to-date.")
            return True # It's successful because there's nothing to do.

    except Exception as e:
        print(f"❌ Error saving to MongoDB: {e}")
        return False
    finally:
        if client:
            client.close()


def GetMongoDBStats() -> None:
    """Display statistics about the MongoDB collection."""
    client = ConnectToMongoDB()
    if not client:
        return

    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]

        total_documents = collection.count_documents({})
        print(f"\n📊 MongoDB Collection Statistics:")
        print(f"   Total articles: {total_documents}")

        pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        source_counts = list(collection.aggregate(pipeline))

        if source_counts:
            print(f"   Articles by source:")
            for source_count in source_counts:
                print(f"     {source_count['_id']}: {source_count['count']}")
    except Exception as e:
        print(f"❌ Error getting MongoDB stats: {e}")
    finally:
        if client:
            client.close()


def ClearMongoDBCollection() -> bool:
    """Clear all documents from the Articles collection."""
    client = ConnectToMongoDB()
    if not client:
        return False

    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]
        result = collection.delete_many({})
        print(f"🗑️  Cleared {result.deleted_count} articles from MongoDB collection")
        return True
    except Exception as e:
        print(f"❌ Error clearing MongoDB collection: {e}")
        return False
    finally:
        if client:
            client.close()


def SearchArticlesBySource(source: str, limit: int = 10) -> List[Dict]:
    """Search articles by source name."""
    client = ConnectToMongoDB()
    if not client:
        return []

    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]
        articles = list(collection.find({"source": source}, {"_id": 0}).limit(limit))
        print(f"🔍 Found {len(articles)} articles from {source}")
        return articles
    except Exception as e:
        print(f"❌ Error searching articles: {e}")
        return []
    finally:
        if client:
            client.close()


def SearchArticlesByDateRange(start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
    """Search articles within a date range."""
    client = ConnectToMongoDB()
    if not client:
        return []

    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        query = {"scraped_at": {"$gte": start_dt, "$lte": end_dt}}
        articles = list(collection.find(query, {"_id": 0}).limit(limit))
        print(f"🔍 Found {len(articles)} articles between {start_date} and {end_date}")
        return articles
    except Exception as e:
        print(f"❌ Error searching articles by date: {e}")
        return []
    finally:
        if client:
            client.close()


def ExportCollectionToJson(filename: str = None) -> bool:
    """Export the entire collection to a JSON file."""
    client = ConnectToMongoDB()
    if not client:
        return False

    try:
        db = client[config.DATABASE_NAME]
        collection = db[config.COLLECTION_NAME]
        articles = list(collection.find({}, {"_id": 0}))

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mongodb_export_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(articles)} articles to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error exporting collection: {e}")
        return False
    finally:
        if client:
            client.close()