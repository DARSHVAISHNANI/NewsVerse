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
user_analysis_col = client["UserDB"]["UserPreferenceAnalysisBasedNER"]
news_col = client["NewsVerseDB"]["NewsVerseCo"]
# recommendations_col = client["RecommendationHistory"]["RecommendedArticle"]

# Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# AI Agent
article_match_agent = Agent(
    name="ArticleRecommenderAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You are an expert news recommendation engine. "
        "You will receive a user preference summary and a shortlist of news articles. "
        "Rank the top 10 articles in order of relevance and return ONLY their `_id`s in a JSON list."
    ),
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)

def suggest_articles_for_user(user_id, detailed_summary, top_n=10):
    """Suggest top N articles for a user using embeddings only."""
    
    # 1. Create embedding for user summary
    summary_embedding = model.encode(detailed_summary)

    # 2. Fetch all articles with stored embeddings
    articles = list(news_col.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "title": 1, "body": 1, "embedding": 1}
    ))

    if not articles:
        return []

    # 3. Compute cosine similarity
    for article in articles:
        article_embedding = np.array(article["embedding"], dtype=np.float32)
        similarity = float(
            np.dot(summary_embedding, article_embedding) /
            (np.linalg.norm(summary_embedding) * np.linalg.norm(article_embedding))
        )
        article["similarity"] = similarity

    # 4. Sort & select top N
    top_articles = sorted(articles, key=lambda x: x["similarity"], reverse=True)[:top_n]

    # 5. Return results (article ID, title, similarity)
    return [
        {"_id": str(a["_id"]), "title": a["title"], "similarity": round(a["similarity"], 4)}
        for a in top_articles
    ]


def recommend_for_all_users():
    """Loop through all users and recommend articles."""
    users = list(user_analysis_col.find({}, {"user_id": 1, "detailed_summary": 1}))
    all_recommendations = []

    for user in users:
        user_id = user["user_id"]
        detailed_summary = user["detailed_summary"]

        print(f"🔍 Processing user: {user_id}")
        top_articles = suggest_articles_for_user(user_id, detailed_summary, top_n=10)

        if top_articles:
            print(f"✅ Top {len(top_articles)} recommendations for {user_id}:")
            for art in top_articles:
                print(f"   {art['_id']} | {art['title']} | score={art['similarity']}")
            all_recommendations.append({"user_id": user_id, "articles": top_articles})
        else:
            print(f"⚠ No recommendation for {user_id}")

    return all_recommendations

if __name__ == "__main__":
    recommend_for_all_users()