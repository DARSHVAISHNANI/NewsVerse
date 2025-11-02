# in whatsapp_recommender/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
# It's highly recommended to store your SID and TOKEN in a .env file
load_dotenv()

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
NEWS_DB_NAME = "TestANewsVerseDB"
NEWS_COLLECTION_NAME = "AC"
USER_DB_NAME = "TestANewsVerseDB"
USER_PREF_COLLECTION_NAME = "UserPreferenceAnalysis"
USER_INFO_COLLECTION_NAME = "UserDetails" # stores user_id + phone_number

# --- Embedding Model Configuration ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Twilio Configuration ---
# Best practice: Load these from environment variables
ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")