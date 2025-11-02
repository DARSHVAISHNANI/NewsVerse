# in ner_processor/config.py

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file
# Try to find .env file in parent directories (backend, or root)
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
else:
    # Fallback: try loading from backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(backend_dir, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        # Last resort: try root directory
        root_dir = os.path.dirname(backend_dir)
        env_file = os.path.join(root_dir, '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()  # Default behavior

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("⚠️ WARNING: MONGO_URI environment variable is not set!")

# --- Database and Collection Names ---
NEWS_DB_NAME = "TestANewsVerseDB"
NEWS_COLLECTION_NAME = "AC"

USER_DB_NAME = "TestANewsVerseDB"
USER_COLLECTION_NAME = "UserDetails"

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")