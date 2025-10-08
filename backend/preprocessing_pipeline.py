import sys
import os

# This allows the script to import modules from your project
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from Embedding_Creation.embeddings import storeArticleEmbeddings
from Name_Entity_Recognition.NER import runNerForUsers
from Recommendation_Engine.engine import main as runRecommendationEngine

def main():
    """
    Runs the full preprocessing pipeline to refresh recommendation data.
    """
    print("🚀 [SCHEDULER] Starting the preprocessing pipeline...")

    print("\n--- 1. Running Embedding Creation ---")
    storeArticleEmbeddings()

    print("\n--- 2. Running NER ---")
    runNerForUsers()

    print("\n--- 3. Running Recommendation Engine (Analysis & Recommendations) ---")
    runRecommendationEngine()

    print("\n✅ [SCHEDULER] Preprocessing pipeline finished!")

if __name__ == "__main__":
    main()