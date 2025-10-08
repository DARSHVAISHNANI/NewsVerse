import json

# Import the modules that contain the logic
from Recommendation_Engine import db_manager
from Recommendation_Engine import user_analyzer
from Recommendation_Engine import article_recommender
from Recommendation_Engine.model_loader import embedding_model

# Note: We no longer import the agents directly in the pipeline file.

def main():
    """
    Runs the full pipeline:
    1. Analyzes user preferences.
    2. Generates article recommendations based on the analysis.
    """
    print("🚀 Starting the full recommendation pipeline...")

    # 1. Connect to all necessary database collections
    (news_collection, user_profiles_collection, 
     user_analysis_collection, user_recommended_articles_collection) = db_manager.connectToDbs()
    
    if any(c is None for c in [news_collection, user_profiles_collection, 
                                user_analysis_collection, user_recommended_articles_collection]):
        print("❌ One or more database collections could not be initialized.")
        return

    # --- PART 1: ANALYZE USER PREFERENCES ---
    print("\n--- Running User Preference Analysis ---")
    # The 'AnalysisAgent' argument is removed. The function now handles agent creation internally.
    analysis_results = user_analyzer.analyzeAllUsers(user_profiles_collection)

    # Save the analysis results to the database
    if analysis_results:
        db_manager.saveUserAnalysis(user_analysis_collection, analysis_results)
        # Also save to a local file for inspection
        with open("user_preference_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved analysis for {len(analysis_results)} users.")

    # --- PART 2: GENERATE ARTICLE RECOMMENDATIONS ---
    print("\n--- Running Article Recommendation ---")
    # This call doesn't change, as it already follows the correct pattern.
    all_recommendations = article_recommender.recommendForAllUsers(
        user_analysis_collection,
        news_collection,
        embedding_model
    )

    # Save recommendations to a local file and DB
    if all_recommendations:
        for reco in all_recommendations:
            db_manager.saveRecommendations(user_recommended_articles_collection, reco['email'], reco['articles'])
        
        with open("article_recommendations.json", "w", encoding="utf-8") as f:
            json.dump(all_recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved final recommendations for {len(all_recommendations)} users to the database and to article_recommendations.json")

    print("\n🎉 Full pipeline completed successfully!")

if __name__ == "__main__":
    main()