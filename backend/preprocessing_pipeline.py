import sys
import os
import logging

# This allows the script to import modules from your project
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from Embedding_Creation.embeddings import storeArticleEmbeddings
from Name_Entity_Recognition.NER import runNerForUsers
from Recommendation_Engine.engine import main as runRecommendationEngine

# --- Logging Setup ---
logger = logging.getLogger("PreprocessingPipeline")
logger.setLevel(logging.INFO)


def main():
    """
    Runs the full preprocessing pipeline to refresh recommendation data.
    """
    try:
        logger.info("Starting the preprocessing pipeline...")

        logger.info("--- 1. Running Embedding Creation ---")
        storeArticleEmbeddings()

        logger.info("--- 2. Running NER ---")
        runNerForUsers()

        logger.info("--- 3. Running Recommendation Engine (Analysis & Recommendations) ---")
        runRecommendationEngine()

        logger.info("Preprocessing pipeline finished successfully!")
        
    except Exception as e:
        logger.error(f"FATAL ERROR in preprocessing pipeline: {e}", exc_info=True)


if __name__ == "__main__":
    main()