import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI")

# Database Names
NEWS_DB_NAME = "TestANewsVerseDB"
USER_DB_NAME = "TestANewsVerseDB"

# Collection Names
NEWS_ARTICLES_COLLECTION = "AC"
USER_PROFILES_COLLECTION = "UserDetails"
USER_ANALYSIS_COLLECTION = "UserPreferenceAnalysis"
USER_RECOMMENDED_ARTICLES_COLLECTION = "UserRecommendedArticles"

# --- Model Configuration ---
# UPDATED: This now matches the model used in the embedding creation script
EMBEDDING_MODEL = "all-mpnet-base-v2" 

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")