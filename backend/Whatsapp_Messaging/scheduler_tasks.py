import sys
import os
import logging

# Add the project root to the Python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Absolute imports
from Recommendation_Engine import db_manager
from Whatsapp_Messaging import recommender
from Whatsapp_Messaging.whatsapp_serice import formatMessage, sendWhatsapp
from Recommendation_Engine.model_loader import embedding_model

# --- Logging Setup ---
logger = logging.getLogger("SchedulerTasks")
logger.setLevel(logging.INFO)


def send_single_user_notification(user_email: str):
    """
    Fetches recommendations for a single user and sends them via WhatsApp.
    This function is designed to be called by a scheduler.
    """
    logger.info(f"Starting scheduled task for user: {user_email}")
    
    # Connect to all necessary database collections
    news_col, user_details_col, user_analysis_col, _ = db_manager.connectToDbs()
    
    if not all(col is not None for col in [news_col, user_details_col, user_analysis_col]):
        logger.error(f"Task failed for {user_email}: Could not connect to DBs.")
        return

    try:
        user_info = user_details_col.find_one({"email": user_email})
        
        if not user_info or not user_info.get("phone_number"):
            logger.error(f"Task failed for {user_email}: User info or phone number not found in UserDetails collection.")
            return
            
        user_name = user_info.get("name", user_email)
        phone_number = user_info["phone_number"]

        user_pref = user_analysis_col.find_one({"email": user_email})
        if not user_pref or not user_pref.get("detailed_summary"):
            logger.warning(f"Task failed for {user_email}: User preference analysis not found.")
            return

        logger.info(f"Processing user {user_name} ({phone_number})")
        detailed_summary = user_pref["detailed_summary"]

        articles_with_embeddings = db_manager.fetchAllArticlesWithEmbeddings(news_col)
        if not articles_with_embeddings:
            logger.info(f"No articles with embeddings found. Exiting task for {user_name}.")
            return

        # --- Recommendation Logic (Replacing the missing function call) ---
        top_10_articles = recommender.recommendArticlesForUser(
            detailed_summary,
            articles_with_embeddings,
            embedding_model,
            top_n=10
        )
        # --- End Recommendation Logic ---
        
        if not top_10_articles:
            logger.info(f"No initial recommendations found for {user_name}.")
            return

        top_10_ids = [a["_id"] for a in top_10_articles]
        scored_articles = list(news_col.find({"_id": {"$in": top_10_ids}}))
        top_3_reranked = recommender.rerankArticles(scored_articles, top_m=3)

        logger.info(f"Sending top {len(top_3_reranked)} articles to {user_name}...")
        for news in top_3_reranked:
            message = formatMessage(news)
            sendWhatsapp(phone_number, message)
            logger.info(f"Sent: {news['title']}")

        logger.info(f"Scheduled task finished for user {user_name}")
        
    except Exception as e:
        logger.error(f"CRITICAL: Unhandled error in scheduled task for {user_email}: {e}", exc_info=True)


if __name__ == "__main__":
    pass