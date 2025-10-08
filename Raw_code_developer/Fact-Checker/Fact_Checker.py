import json
import os
import re
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.webbrowser import WebBrowserTools
from agno.tools.website import WebsiteTools

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client["NewsVerseDB"]
collection = db["NewsVerseCo"]

print(f"✅ Connected to DB: {db.name}, collection: {collection.name}")

# Fact Checker Agent
FactCheckerAgent = Agent(
    name="FactCheckerAgent",
    model=Gemini(id="gemini-2.0-flash"),
    description="Fact-check an article by extracting its main factual claim and verifying it with a single web search.",
    instructions=[
        "Step 1: Read the provided news article text.",
        "Step 2: Extract the main factual claim from the article.",
        "Step 3: Use ONLY ONE search (DuckDuckGo, GoogleSearch, WebBrowser, or WebsiteTools) for that claim.",
        "Step 4: Compare the claim to the top 3 reputable search results (BBC, Reuters, AP, Bloomberg, etc.).",
        "Step 5: Decide if the claim is factually correct.",
        "Step 6: Output ONLY in JSON format with fields: llm_verdict (true or false), fact_check_explanation (short reason)."
    ],
    tools=[DuckDuckGoTools(), GoogleSearchTools(), WebBrowserTools(), WebsiteTools()],
    markdown=False,
    show_tool_calls=True,
    monitoring=True
)

def run_fact_checker():
    results = []
    
    articles = list(collection.find({}))
    print(f"📦 Found {len(articles)} articles in DB.")

    if not articles:
        print("⚠️ No articles found in DB, using dummy article for testing.")
        articles = [{"_id": "dummy1", "body": "Apple Inc. reported record revenue of $120 billion in Q4 2024."}]

    for article in articles:
        article_id = str(article["_id"])
        article_text = article.get("body", "")

        if not article_text.strip():
            print(f"⏭️ Skipping article {article_id} (empty content).")
            continue

        print(f"🔍 Fact-checking article {article_id}...")

        try:
            response = FactCheckerAgent.run(article_text)
            raw_content = response.content
            print("📝 Raw Agent Response:", raw_content)

            if isinstance(raw_content, str):
                clean_json_str = re.sub(r"^```[a-zA-Z]*\n?", "", raw_content.strip())
                clean_json_str = re.sub(r"\n?```$", "", clean_json_str.strip())
                fact_result = json.loads(clean_json_str)
            else:
                fact_result = raw_content

            results.append({
                "article_id": article_id,
                "llm_verdict": fact_result.get("llm_verdict"),
                "fact_check_explanation": fact_result.get("fact_check_explanation")
            })

            # --- Merge new fact check with existing one to preserve user_verdict ---
            existing_fact_check = article.get("fact_check", {})
            merged_fact_check = {**existing_fact_check, **fact_result}

            # --- Update DB (comment this block out if not updating DB now) ---
            # collection.update_one(
            #     {"_id": article["_id"]},
            #     {"$set": {"fact_check": merged_fact_check}}
            # )

            print(f"✅ Fact check result for article {article_id}: {merged_fact_check}")

        except Exception as e:
            print(f"❌ Error on article {article_id}: {e}")

    # Save results to JSON file
    output_file = "fact_check_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"💾 Results saved to {output_file}")

if __name__ == "__main__":
    run_fact_checker()