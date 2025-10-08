# in ner_processor/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")

# --- Database and Collection Names ---
NEWS_DB_NAME = "TestANewsVerseDB"
NEWS_COLLECTION_NAME = "ArticlesCollection"

USER_DB_NAME = "TestANewsVerseDB"
USER_COLLECTION_NAME = "UserDetails"

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")