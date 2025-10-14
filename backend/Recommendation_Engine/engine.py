import json
import logging

# Import the modules that contain the logic
from Recommendation_Engine import db_manager
from Recommendation_Engine import user_analyzer
from Recommendation_Engine import article_recommender
from Recommendation_Engine.model_loader import embedding_model

# --- Logging Setup ---
logger = logging.getLogger("RecommendationEngine")
logger.setLevel(logging.INFO)

def main():
    """
    Runs the full pipeline:
    1. Analyzes user preferences.
    2. Generates article recommendations based on the analysis.
    """
    logger.info("Starting the full recommendation pipeline...")

    # 1. Connect to all necessary database collections
    (news_collection, user_profiles_collection, 
     user_analysis_collection, user_recommended_articles_collection) = db_manager.connectToDbs()
    
    if any(c is None for c in [news_collection, user_profiles_collection, 
                                user_analysis_collection, user_recommended_articles_collection]):
        logger.critical("One or more database collections could not be initialized.")
        return

    # --- PART 1: ANALYZE USER PREFERENCES ---
    logger.info("--- Running User Preference Analysis ---")
    analysis_results = user_analyzer.analyzeAllUsers(user_profiles_collection)

    # Save the analysis results to the database
    if analysis_results:
        db_manager.saveUserAnalysis(user_analysis_collection, analysis_results)
        logger.info(f"Saved analysis for {len(analysis_results)} users to the database.")

    # --- PART 2: GENERATE ARTICLE RECOMMENDATIONS ---
    logger.info("--- Running Article Recommendation ---")
    all_recommendations = article_recommender.recommendForAllUsers(
        user_analysis_collection,
        news_collection,
        embedding_model
    )

    # Save recommendations to DB
    if all_recommendations:
        for reco in all_recommendations:
            db_manager.saveRecommendations(user_recommended_articles_collection, reco['email'], reco['articles'])
        
        logger.info(f"Saved final recommendations for {len(all_recommendations)} users to the database.")

    logger.info("Full pipeline completed successfully!")

if __name__ == "__main__":
    main()