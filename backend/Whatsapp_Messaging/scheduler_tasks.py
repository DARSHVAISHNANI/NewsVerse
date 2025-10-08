import sys
import os

# Add the project root to the Python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Recommendation_Engine import db_manager
from Whatsapp_Messaging import recommender
from Whatsapp_Messaging.whatsapp_serice import formatMessage, sendWhatsapp
from Recommendation_Engine.model_loader import embedding_model


def send_single_user_notification(user_email: str):
    """
    Fetches recommendations for a single user and sends them via WhatsApp.
    This function is designed to be called by a scheduler.
    """
    print(f"🚀 Starting scheduled task for user: {user_email}")
    
    # UPDATED: Renamed variables for clarity to prevent mix-ups
    news_col, user_details_col, user_analysis_col, _ = db_manager.connectToDbs()
    
    if not all(col is not None for col in [news_col, user_details_col, user_analysis_col]):
        print(f"❌ Task failed for {user_email}: Could not connect to DBs.")
        return

    # UPDATED: Correctly query the 'user_details_col' (UserDetails collection)
    user_info = user_details_col.find_one({"email": user_email})
    
    if not user_info or not user_info.get("phone_number"):
        print(f"❌ Task failed for {user_email}: User info or phone number not found in UserDetails collection.")
        return
        
    user_name = user_info.get("name", user_email)
    phone_number = user_info["phone_number"]

    # UPDATED: Correctly query the 'user_analysis_col' (UserPreferenceAnalysis collection)
    user_pref = user_analysis_col.find_one({"email": user_email})
    if not user_pref or not user_pref.get("detailed_summary"):
        print(f"❌ Task failed for {user_email}: User preference analysis not found.")
        return

    print(f"🔍 Processing user {user_name} ({phone_number})")
    detailed_summary = user_pref["detailed_summary"]

    articles_with_embeddings = db_manager.fetchAllArticlesWithEmbeddings(news_col)
    if not articles_with_embeddings:
        print(f"ℹ️ No articles with embeddings found. Exiting task for {user_name}.")
        return

    top_10_articles = recommender.recommendArticlesForUser(
        detailed_summary,
        articles_with_embeddings,
        embedding_model,
        top_n=10
    )
    if not top_10_articles:
        print(f"  - No initial recommendations found for {user_name}.")
        return

    top_10_ids = [a["_id"] for a in top_10_articles]
    scored_articles = list(news_col.find({"_id": {"$in": top_10_ids}}))
    top_3_reranked = recommender.rerankArticles(scored_articles, top_m=3)

    print(f"  - Sending top {len(top_3_reranked)} articles to {user_name}...")
    for news in top_3_reranked:
        message = formatMessage(news)
        sendWhatsapp(phone_number, message)
        print(f"    ✅ Sent: {news['title']}")

    print(f"✅ Scheduled task finished for user {user_name}")