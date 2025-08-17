import json
import numpy as np
from pymongo import MongoClient
import certifi
from sentence_transformers import SentenceTransformer
from twilio.rest import Client

# -------------------------------
# MongoDB Setup
# -------------------------------
mongo_client = MongoClient(
    "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/",
    tlsCAFile=certifi.where()
)
db = mongo_client["NewsVerseDB"]
news_col = db["NewsVerseCo"]

user_db = mongo_client["UserDB"]
user_pref_col = user_db["UserPreferenceAnalysisBasedNER"]
user_co_col = user_db["UserCoUpdation"]   # stores user_id + phone_number

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# Twilio Setup
# -------------------------------
ACCOUNT_SID = "AC1d5ab7898f9f098146c40cfff1a37a7c"
AUTH_TOKEN = "c205c6741c7d7db385d66a7d7470b956"
FROM_WHATSAPP = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# -------------------------------
# Format WhatsApp message
# -------------------------------
def format_message(news):
    return f"""
📰 *Big News:* {news.get('title','')}

👉 {news.get('summarization',{}).get('summary','No summary')}

📌 *Fact-Check:* {'✅ Verified' if news.get('fact_check',{}).get('verdict', False) else '❌ Not Verified'}
😊 *Sentiment:* {news.get('sentiment','Unknown')}

📅 {news.get('date','')} | Source: {news.get('source','')}
🔗 Full story: {news.get('url','')}
"""

def send_whatsapp(user_number, message):
    twilio_client.messages.create(
        from_=FROM_WHATSAPP,
        to=f"whatsapp:{user_number}",
        body=message
    )

# -------------------------------
# Agent 1: Recommend Top 10 (Embeddings)
# -------------------------------
def recommend_articles_for_user(detailed_summary, top_n=10):
    summary_embedding = model.encode(detailed_summary)

    articles = list(news_col.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "title": 1, "embedding": 1}
    ))

    if not articles:
        return []

    for article in articles:
        article_embedding = np.array(article["embedding"], dtype=np.float32)
        similarity = float(
            np.dot(summary_embedding, article_embedding) /
            (np.linalg.norm(summary_embedding) * np.linalg.norm(article_embedding))
        )
        article["similarity"] = similarity

    top_articles = sorted(articles, key=lambda x: x["similarity"], reverse=True)[:top_n]
    return top_articles

# -------------------------------
# Agent 2: Sort Top 10 by final_custom_score
# -------------------------------
def rerank_articles(top_articles, top_m=3):
    ids = [a["_id"] for a in top_articles]

    # Fetch full documents with scores
    scored_articles = list(news_col.find(
        {"_id": {"$in": ids}},
        {"title": 1, "summarization": 1, "fact_check": 1, "sentiment": 1, 
         "date": 1, "source": 1, "url": 1, "article_score.final_custom_score": 1}
    ))

    # Sort by final_custom_score
    scored_articles = sorted(
        scored_articles, 
        key=lambda x: x.get("article_score", {}).get("final_custom_score", 0), 
        reverse=True
    )

    return scored_articles[:top_m]

# -------------------------------
# Main Pipeline
# -------------------------------
def push_recommendations_to_users():
    users = list(user_pref_col.find({}, {"user_id": 1, "detailed_summary": 1}))

    for user in users:
        uid = user["user_id"]
        detailed_summary = user["detailed_summary"]

        # 1. Get user phone number
        user_doc = user_co_col.find_one({"user_id": uid}, {"phone_number": 1})
        if not user_doc or "phone_number" not in user_doc:
            print(f"⚠ Skipping {uid}, no phone number found")
            continue

        phone_number = user_doc["phone_number"]

        print(f"\n🔍 Processing user {uid} ({phone_number})")

        # 2. Agent 1: Recommend top 10
        top_articles = recommend_articles_for_user(detailed_summary, top_n=10)

        if not top_articles:
            print(f"⚠ No recommendations for {uid}")
            continue

        # 3. Agent 2: Rerank & pick top 3
        top3 = rerank_articles(top_articles, top_m=3)

        # 4. Send via WhatsApp
        for news in top3:
            msg = format_message(news)
            send_whatsapp(phone_number, msg)
            print(f"✅ Sent to {uid}: {news['title']}")

if __name__ == "__main__":
    push_recommendations_to_users()