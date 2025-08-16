import os
import certifi
import json
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
import re

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
news_db = client["NewsVerseDB"]
news_collection = news_db["NewsVerseCo"]
user_db = client["UserDB"]
user_collection = user_db["UserCo"]

# Set up the Agno Gemini agent for NER extraction
ner_agent = Agent(
    name="NERGeminiAgent",
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    instructions=(
        "Extract all unique named entities from the following news article text and categorize them "
        'as "Person", "Location" (including cities/countries/regions), or "Organization" (companies, institutions). '
        "Return strictly a JSON object in this format:\n"
        "{\n"
        '  "Person": [list of unique person names],\n'
        '  "Location": [list of unique locations],\n'
        '  "Organization": [list of unique organizations]\n'
        "}\n"
        "Do not include any other text, comments, or explanations. Return valid JSON only."
    ),
    markdown=False
)

def run_ner_for_users():
    users_cursor = user_collection.find({})
    for user in users_cursor:
        user_id = user.get("user_id")
        title_ids = user.get("title_id_list", [])
        ner_result = {"Person": set(), "Location": set(), "Organization": set()}

        for aid in title_ids:
            try:
                article = news_collection.find_one({"_id": ObjectId(aid)})
            except Exception:
                print(f"❗ Invalid ObjectId {aid}, skipping.")
                continue
            if not article or not article.get("body"):
                print(f"⚠ Article {aid} missing content, skipping.")
                continue

            try:
                response = ner_agent.run(article["content"])
                raw_output = response.content
                print(f"[DEBUG] Raw Gemini output for article {aid}:\n{raw_output!r}")

                # Clean output: remove possible code fences and whitespace
                cleaned = re.sub(r"^`{3,}[a-zA-Z]*\n?", "", raw_output.strip())
                cleaned = re.sub(r"\n?`{3,}$", "", cleaned)
                cleaned = cleaned.strip()

                # Defensive check: must start and end with braces for JSON
                if not cleaned.startswith("{") or not cleaned.endswith("}"):
                     print(f"❗ NER output for article {aid} not valid JSON:\n{cleaned}")
                     continue

                ner_json = json.loads(cleaned)

                for entity_type in ner_result:
                    entities = ner_json.get(entity_type, [])
                    if isinstance(entities, list):
                        ner_result[entity_type].update(e.strip() for e in entities if isinstance(e, str))

            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error for article {aid}: {e}\nOutput:\n{cleaned}")
            except Exception as e:
                print(f"❌ Error during NER for article {aid}: {e}")

        # Convert sets to sorted lists before saving
        ner_doc = {k: sorted(v) for k, v in ner_result.items()}
        user_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"NER": ner_doc}}
        )
        print(f"✅ Updated NER for user '{user_id}': {ner_doc}")

    client.close()
    print("🔒 MongoDB connection closed.")

if _name_ == "_main_":
    run_ner_for_users()