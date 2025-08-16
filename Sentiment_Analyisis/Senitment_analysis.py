import os
import json
import re
from pymongo import MongoClient
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# MongoDB connection
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "NewsVerseDB"
COLLECTION_NAME = "NewsVerseCo"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -----------------------------
# Sentiment Analysis Agent (JSON output)
# -----------------------------
sentiment_agent = Agent(
    name="Sentiment Agent",
    description="Analyze the content of news articles and determine their sentiment.",
    instructions="""
    You are a sentiment evaluation agent. Analyze the tone and language of the article text.  
    Determine sentiment strictly as **Positive, Negative, or Neutral** based on these rules:

    1. **Positive** → The article contains positive keywords (e.g., growth, profit, gain, recovery, expansion, strong, successful), or the overall tone is optimistic and confidence-building.  
    2. **Negative** → The article contains negative keywords (e.g., loss, decline, fall, risk, weak, downgrade, failure), or the overall tone is pessimistic, warning, or confidence-reducing.  
    3. **Neutral** → The article is mainly factual, descriptive, or balanced — with no clear positive or negative tone. Includes objective reporting, announcements, or mixed signals.  
    4. Return only JSON in this exact format:

    {
        "sentiment": "<Positive|Negative|Neutral>",
        "reason": "<short reason explaining the classification>"
    }

    5. Reason should be brief (1-2 sentences).  
    6. Do NOT include anything outside the JSON object.

    Input: The article text will be provided. Analyze carefully and return ONLY the JSON object.
    """,
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    debug_mode=True,
    markdown=True
)

# -----------------------------
# Helper functions
# -----------------------------
def clean_json_output(text: str) -> str:
    """Remove Markdown code fences and extra whitespace from LLM output."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def debug_print_article(article, content):
    print("\n" + "="*80)
    print(f"[DEBUG] Processing Article ID: {article.get('_id')}")
    print(f"[DEBUG] Title: {article.get('title', '[No Title]')}")
    print(f"[DEBUG] Content length: {len(content)} characters")
    print("="*80 + "\n")

def debug_print_response(raw_text, cleaned_text):
    print("\n[DEBUG] Raw Agent Content:")
    print(raw_text)
    print("-"*50)
    print("[DEBUG] Cleaned JSON Text:")
    print(cleaned_text)
    print("-"*50)

def debug_print_parsed(sentiment_data, fallback=False):
    if fallback:
        print(f"[DEBUG] JSON parsing failed. Falling back to Neutral sentiment.")
    else:
        print(f"[DEBUG] Parsed JSON Data: {sentiment_data}")

# -----------------------------
# Fetch articles without sentiment
# -----------------------------
articles = collection.find({
    "$or": [
        {"sentiment": {"$exists": True}},
        {"sentiment": None},
        {"sentiment": ""}
    ]
})

update_db = True  # Set True to save back to MongoDB
json_results = []

for article in articles:
    content = article.get("body", "")
    if not content.strip():
        print(f"[DEBUG] Skipping article '{article.get('title', '[No Title]')}' because content is empty.")
        continue

    # Debug: print article info
    debug_print_article(article, content)

    # Run sentiment analysis
    response_obj = sentiment_agent.run(content)
    raw_text = response_obj.content

    # Clean Markdown code fences
    cleaned_text = clean_json_output(raw_text)

    # Debug: print raw and cleaned response
    debug_print_response(raw_text, cleaned_text)

    # Parse JSON safely
    try:
        sentiment_data = json.loads(cleaned_text)
        sentiment = sentiment_data.get("sentiment", "Neutral")
        reason = sentiment_data.get("reason", "")
        debug_print_parsed(sentiment_data)
    except json.JSONDecodeError:
        sentiment = "Neutral"
        reason = "Failed to parse LLM output."
        debug_print_parsed(None, fallback=True)

    # Validate sentiment
    if sentiment not in ["Positive", "Negative", "Neutral"]:
        print(f"[DEBUG] ⚠️ Unexpected sentiment output: '{sentiment}', defaulting to Neutral")
        sentiment = "Neutral"

    print(f"[DEBUG] Final Sentiment: {sentiment}")
    print(f"[DEBUG] Reason: {reason}")

    # Save sentiment back to MongoDB (if enabled)
    if update_db:
        collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"sentiment": sentiment}}
        )
        print(f"[DEBUG] ✅ Updated article '{article.get('title')}' with sentiment: {sentiment}")
    else:
        print("[DEBUG] ℹ Skipped updating MongoDB (debug mode).")

    # Save result to JSON list
    json_results.append({
        "article_id": str(article["_id"]),
        "title": article.get("title"),
        "sentiment": sentiment,
        "reason": reason
    })

# Save all results to a JSON file
if json_results:
    filename = "sentiment_results.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=4, ensure_ascii=False)
    print(f"\n[DEBUG] ✅ Saved {len(json_results)} sentiment results to '{filename}'")

client.close()
print("\n[DEBUG] All done!")