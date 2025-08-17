import os
import json
import re
from pymongo import MongoClient
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
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
# Summarization Agent
# -----------------------------
summarization_agent = Agent(
    name="Summarization Agent",
    description="Summarize news articles into concise, clear summaries.",
    instructions="""
    You are a news article summarizer. Summarize the given article text in 2-4 sentences.

    Return JSON in this exact format:
    {
        "summary": "<short, concise summary of the article>"
    }

    Do NOT include anything outside the JSON object.
    """,
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    debug_mode=True,
    markdown=True
)

# -----------------------------
# Storytelling Summarization Agent
# -----------------------------
story_agent = Agent(
    name="Storytelling Summarizer",
    description="Summarize news articles in a fun, simple story-like way for children.",
    instructions="""
    You are a children's story writer. Read the article carefully and summarize it in a fun, simple, and easy-to-read way for kids.

    Rules:
    1. Use simple language suitable for 6-12 year old children.
    2. Make it engaging like a short story.
    3. Keep the summary concise (3-5 sentences max).
    4. Focus on the main events or important points, but avoid technical jargon.
    5. Return JSON in this exact format:

    {
        "story_summary": "<summary written as a story for kids>"
    }

    6. Do NOT include anything outside the JSON object.
    """,
    model=Groq(id="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY")),
    debug_mode=True,
    markdown=True
)

# -----------------------------
# Helper function to clean JSON output
# -----------------------------
def clean_json_output(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text)
    return text.strip()

# -----------------------------
# Fetch articles without summaries
# -----------------------------
articles = list(collection.find({
    "$or": [
        {"summarization": {"$exists": False}},
        {"story_summarization": {"$exists": False}}
    ]
}))

json_results = []

# -----------------------------
# Process each article
# -----------------------------
for article in articles:
    content = article.get("body", "")
    if not content.strip():
        print(f"[DEBUG] Skipping article '{article.get('title', '[No Title]')}' because content is empty.")
        continue

    print("\n" + "="*80)
    print(f"[DEBUG] Processing Article ID: {article.get('_id')}")
    print(f"[DEBUG] Title: {article.get('title', '[No Title]')}")
    print(f"[DEBUG] Content length: {len(content)} characters")
    print("="*80 + "\n")

    # -----------------------------
    # Factual summarization
    # -----------------------------
    response_obj = summarization_agent.run(content)
    raw_text = response_obj.content
    cleaned_text = clean_json_output(raw_text)
    
    try:
        summary_data = json.loads(cleaned_text)
        summary_text = summary_data.get("summary", "")
        print(f"[DEBUG] Factual Summary: {summary_text}")
    except json.JSONDecodeError:
        summary_text = ""
        print(f"[DEBUG] Failed to parse factual summary for article '{article.get('title')}'")

    # -----------------------------
    # Storytelling summarization
    # -----------------------------
    story_response = story_agent.run(content)
    story_raw = story_response.content
    story_cleaned = clean_json_output(story_raw)

    try:
        story_data = json.loads(story_cleaned)
        story_text = story_data.get("story_summary", "")
        print(f"[DEBUG] Story Summary: {story_text}")
    except json.JSONDecodeError:
        story_text = ""
        print(f"[DEBUG] Failed to parse story summary for article '{article.get('title')}'")

    # -----------------------------
    # Update MongoDB with nested fields
    # -----------------------------
    collection.update_one(
        {"_id": article["_id"]},
        {"$set": {
            "summarization": {
                "summary": summary_text,
                "story_summary": story_text
            }
        }}
    )
    print(f"[DEBUG] ✅ Updated article '{article.get('title')}' with both summaries.")

    # -----------------------------
    # Save results to JSON list
    # -----------------------------
    json_results.append({
        "article_id": str(article["_id"]),
        "title": article.get("title"),
        "summarization": {
            "summary": summary_text,
            "story_summary": story_text
        },
    })

# -----------------------------
# Save all results to a JSON file
# -----------------------------
if json_results:
    filename = "combined_article_summaries.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=4, ensure_ascii=False, default=str)
    print(f"[DEBUG] ✅ Saved {len(json_results)} combined summaries to '{filename}'")

client.close()
print("\n[DEBUG] All done!")