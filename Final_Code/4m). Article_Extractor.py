from agno.agent import Agent
from agno.models.google import Gemini
from pymongo import MongoClient
import certifi
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# MongoDB Setup
# -----------------------------
client = MongoClient(
    "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/",
    tlsCAFile=certifi.where()
)
user_analysis_col = client["UserDB"]["UserPreferenceAnalysis"]
news_col = client["NewsVerseDB"]["NewsVerseCo"]
recommendations_col = client["UserDB"]["UserArticleRecommendations"]

# Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# AI Agent
article_match_agent = Agent(
    name="ArticleRecommenderAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You are an expert news recommendation engine. "
        "You will receive a user preference summary and a shortlist of news articles. "
        "Select the most relevant one and return ONLY the `_id` of that article."
    ),
    add_history_to_messages=False,
    markdown=False,
    debug_mode=True,
    show_tool_calls=True
)

def suggest_article_for_user(user_id, detailed_summary, top_n=5):
    """Suggest best article for a single user."""
    # Embed user summary
    summary_embedding = model.encode(detailed_summary)

    # Fetch articles with embeddings
    articles = list(news_col.find({"embedding": {"$exists": True}}, {"_id": 1, "title": 1, "body": 1, "embedding": 1}))

    if not articles:
        return None

    # Compute similarity
    for article in articles:
        article["similarity"] = float(
            np.dot(summary_embedding, article["embedding"]) /
            (np.linalg.norm(summary_embedding) * np.linalg.norm(article["embedding"]))
        )

    # Sort and shortlist top N
    top_articles = sorted(articles, key=lambda x: x["similarity"], reverse=True)[:top_n]

    # Prepare JSON for AI
    articles_json = json.dumps(
        [{"_id": str(a["_id"]), "title": a["title"], "body": a["body"]} for a in top_articles],
        ensure_ascii=False
    )

    # Ask AI agent
    prompt = f"""
    User summary:
    {detailed_summary}

    Shortlisted Articles:
    {articles_json}

    Please return ONLY the _id of the best matching article.
    """
    result = article_match_agent.run(prompt)
    return result.content.strip()

def recommend_for_all_users():
    """Loop through all users and recommend articles."""
    users = list(user_analysis_col.find({}, {"user_id": 1, "detailed_summary": 1}))
    all_recommendations = []

    for user in users:
        user_id = user["user_id"]
        detailed_summary = user["detailed_summary"]

        print(f"🔍 Processing user: {user_id}")
        article_id = suggest_article_for_user(user_id, detailed_summary)

        if article_id:
            print(f"✅ Recommended article for {user_id}: {article_id}")
            all_recommendations.append({"user_id": user_id, "article_id": article_id})
        else:
            print(f"⚠ No recommendation for {user_id}")

    # Save recommendations in DB
    # if all_recommendations:
    #     recommendations_col.delete_many({})  # Optional: clear old results
    #     recommendations_col.insert_many(all_recommendations)
    #     print(f"\n💾 Saved {len(all_recommendations)} recommendations to DB.")

if __name__ == "__main__":
    recommend_for_all_users()