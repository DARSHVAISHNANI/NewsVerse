# backend/Sentiment_Analysis/config.py
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "TestANewsVerseDB"
COLLECTION_NAME = "AC"

# No database client is initialized here