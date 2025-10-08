# in whatsapp_recommender/run_whatsapp_sender.py

# Import from our new modules
from Whatsapp_Messaging import db_manager
from Whatsapp_Messaging import whatsapp_service
from Whatsapp_Messaging import recommender
from Recommendation_Engine.model_loader import embedding_model

def pushRecommendationsToUsers():
    """Main function to generate and send recommendations to users via WhatsApp."""

    # 1. Connect to all necessary database collections
    news_col, user_pref_col, user_info_col = db_manager.connectToDbs()
    if not all([news_col, user_pref_col, user_info_col]):
        print("❌ Pipeline failed: Could not connect to databases.")
        return

    # 2. Fetch all users and articles with embeddings once to be efficient
    users = db_manager.fetchAllUsersForRecommendation(user_pref_col)
    articles_with_embeddings = db_manager.fetchAllArticlesWithEmbeddings(news_col)

    if not users:
        print("ℹ️ No users with preference analysis found. Exiting.")
        return
    if not articles_with_embeddings:
        print("ℹ️ No articles with embeddings found. Exiting.")
        return

    # 3. Process each user
    for user in users:
        uid = user["user_id"]
        detailed_summary = user["detailed_summary"]

        # 4. Get the user's phone number
        phone_number = db_manager.fetchUserPhoneNumber(user_info_col, uid)
        if not phone_number:
            print(f"⚠️  Skipping user {uid}, no phone number found.")
            continue

        print(f"\n🔍 Processing user {uid} ({phone_number})")

        # 5. Agent 1: Recommend top 10 articles using embeddings
        top_10_articles = recommender.recommendArticlesForUser(
            detailed_summary, 
            articles_with_embeddings, 
            embedding_model, 
            top_n=10
        )

        if not top_10_articles:
            print(f"  - No initial recommendations found for {uid}.")
            continue

        # 6. Fetch full data for the top 10 to prepare for re-ranking
        top_10_ids = [a["_id"] for a in top_10_articles]
        scored_articles = db_manager.fetchFullArticlesByIds(news_col, top_10_ids)

        # 7. Agent 2: Rerank the top 10 to get the top 3
        top_3_reranked = recommender.rerankArticles(scored_articles, top_m=3)

        # 8. Format and send the top 3 articles via WhatsApp
        print(f"  - Sending top {len(top_3_reranked)} articles to {uid}...")
        for news in top_3_reranked:
            message = whatsapp_service.formatMessage(news)
            whatsapp_service.sendWhatsapp(phone_number, message)
            print(f"    ✅ Sent: {news['title']}")

    print("\n🎉 WhatsApp recommendation pipeline finished for all users!")

if __name__ == "__main__":
    pushRecommendationsToUsers()