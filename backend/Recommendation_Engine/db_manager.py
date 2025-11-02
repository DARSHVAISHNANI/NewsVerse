# in recommendation_engine/db_manager.py

import certifi
from pymongo import MongoClient
from Recommendation_Engine import config

def connectToDbs():
    """
    Connects to MongoDB and returns the four key collection objects.
    """
    try:
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
        news_db = client[config.NEWS_DB_NAME]
        news_collection = news_db[config.NEWS_ARTICLES_COLLECTION]
        user_db = client[config.USER_DB_NAME]
        user_profiles_collection = user_db[config.USER_PROFILES_COLLECTION]
        user_analysis_collection = user_db[config.USER_ANALYSIS_COLLECTION]
        user_recommended_articles_collection = user_db[config.USER_RECOMMENDED_ARTICLES_COLLECTION]
        print("✅ Successfully connected to all DB collections.")
        return news_collection, user_profiles_collection, user_analysis_collection, user_recommended_articles_collection
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None, None, None, None

def fetchAllUsersForAnalysis(user_profiles_collection):
    """Fetches name, email, title_list, ner_data, and _id from the main user collection."""
    if user_profiles_collection is None:
        return []
    # FIXED: Changed "NER" to "ner_data" to match what NER module saves, and include _id for user_id
    return list(user_profiles_collection.find({}, {"name": 1, "email": 1, "title_list": 1, "ner_data": 1, "_id": 1}))

def saveUserAnalysis(user_analysis_collection, analysis_results):
    """Deletes old analysis and inserts the new results."""
    if user_analysis_collection is None:
        return
    user_analysis_collection.delete_many({})
    # FIXED: Changed from attribute access (r.email) to dictionary access (r["email"])
    # since user_analyzer returns dictionaries, not objects
    user_analysis_collection.insert_many([
        {"email": r["email"], "name": r["name"], "detailed_summary": r["detailed_summary"]}
        for r in analysis_results
    ])
    print(f"💾 Saved analysis for {len(analysis_results)} users to the database.")

def fetchAllUsersForRecommendation(user_analysis_collection):
    """Fetches user's email and their detailed summary from the analysis collection."""
    if user_analysis_collection is None:
        return []
    return list(user_analysis_collection.find({}, {"email": 1, "name": 1, "detailed_summary": 1}))

def fetchAllArticlesWithEmbeddings(news_collection):
    """Fetches all news articles that have an embedding vector."""
    if news_collection is None:
        return []
    return list(news_collection.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "title": 1, "content": 1, "embedding": 1}
    ))

def saveRecommendations(recommendations_collection, user_email, recommended_articles):
    """Saves or updates the recommended articles for a specific user."""
    if recommendations_collection is None:
        return
    recommendations_collection.update_one(
        {"email": user_email},
        {"$set": {"articles": recommended_articles}},
        upsert=True
    )