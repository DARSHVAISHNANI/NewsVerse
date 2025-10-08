# config.py

import os
from dotenv import load_dotenv, find_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv(find_dotenv())

# -----------------------------
# MongoDB Configuration
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "TestANewsVerseDB"
COLLECTION_NAME = "ArticlesCollection"

# -----------------------------
# API Keys (It's good practice to load them here too)
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")