# in article_scorer/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "TestANewsVerseDB"
COLLECTION_NAME = "AC"