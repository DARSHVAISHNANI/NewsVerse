import json
import re
import os
from pymongo import MongoClient
import certifi
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# MongoDB Connection
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
news_col = client["NewsVerseDB"]["NewsVerseCo"]

# -----------------------------
# AI Agent Setup
# -----------------------------
article_scorer_agent = Agent(
    name="ArticleScorerAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions="""
    You are an evaluator of news articles.
    Score each article from 0 to 9 based on knowledge depth:

    0–2: Poor — highly superficial, incomplete, or factually questionable.
    3–5: Moderate — covers basics but lacks depth or misses key points.
    6–8: Good — detailed, covers multiple aspects, balanced and factual.
    9: Exceptional — comprehensive, in-depth, authoritative, and well-structured.

    Return valid JSON only in the format:
    {
    "score": <integer 0–9>,
    "reason": "<short reason>"
    }
    """,
    add_history_to_messages=False,
    markdown=False,
    debug_mode=False
)

# -----------------------------
# JSON Repair Helper
# -----------------------------
def repair_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    seen = set()
    lines = []
    for line in text.splitlines():
        match = re.match(r'\s*"(\w+)"\s*:', line)
        if match:
            key = match.group(1)
            if key in seen:
                continue
            seen.add(key)
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)

    return text

# -----------------------------
# Scoring Function
# -----------------------------
def score_all_articles():
    articles = list(news_col.find({}))
    results_list = []
    count = 0

    # Group articles by title
    articles_by_title = {}
    for art in articles:
        title = art.get("title", "").strip().lower()
        if not title:
            continue
        if title not in articles_by_title:
            articles_by_title[title] = []
        articles_by_title[title].append(art)

    # Process each grouped title
    for title, docs in articles_by_title.items():
        reason = "No reason provided."
        user_score = None

        # Get user_article_score if exists
        for doc in docs:
            if "article_score" in doc and isinstance(doc["article_score"], dict):
                if "user_article_score" in doc["article_score"]:
                    user_score = doc["article_score"]["user_article_score"]
                    break

        # Always get fresh llm_score
        doc = docs[0]  # pick one representative article
        article_text = f"{doc.get('title', '')}\n\n{doc.get('body', '')}"
        result = article_scorer_agent.run(article_text)
        print(result)
        output_text = repair_json(result.content.strip())

        try:
            score_data = json.loads(output_text)
            llm_score = int(score_data.get("score", 0))
            reason = score_data.get("reason", "No reason provided.")
        except json.JSONDecodeError:
            print(f"❌ Could not parse JSON for article {doc['_id']}: {output_text}")
            continue

        # Compute custom final score
        if user_score is not None:
            final_score = round((llm_score * 0.6) + (user_score * 0.4), 2)
        else:
            final_score = llm_score

        # Store in all docs with this title
        for doc in docs:
            news_col.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "article_score": {
                        "user_article_score": user_score,
                        "llm_score": llm_score,
                        "final_custom_score": final_score
                    }
                }}
            )

        # Save for JSON file
        results_list.append({
            "title": title,
            "user_article_score": user_score,
            "llm_score": llm_score,
            "final_custom_score": final_score,
            "score_reason": reason,
            "scored_by": "Gemini-2.0-flash"
        })
        count += 1

    # Save JSON results
    if results_list:
        filename = "article_scores.json"
        old_data = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        old_data.extend(results_list)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Processed {count} grouped articles. Saved to {filename}")
    else:
        print("ℹ No articles processed.")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    score_all_articles()