# in whatsapp_recommender/recommender.py

import numpy as np

def recommendArticlesForUser(user_summary: str, all_articles: list, embedding_model, top_n: int = 10):
    """Finds the top N most similar articles using embeddings."""

    summary_embedding = embedding_model.encode(user_summary)

    if not all_articles:
        return []

    for article in all_articles:
        article_embedding = np.array(article["embedding"], dtype=np.float32)
        # Handle potential zero vectors
        norm_summary = np.linalg.norm(summary_embedding)
        norm_article = np.linalg.norm(article_embedding)
        if norm_summary == 0 or norm_article == 0:
            similarity = 0.0
        else:
            similarity = float(
                np.dot(summary_embedding, article_embedding) / (norm_summary * norm_article)
            )
        article["similarity"] = similarity

    top_articles = sorted(all_articles, key=lambda x: x["similarity"], reverse=True)[:top_n]
    return top_articles

def rerankArticles(scored_articles: list, top_m: int = 3):
    """Sorts a list of articles by their final_custom_score."""

    # Sort by the final_custom_score, with a default of 0 if the score is missing
    reranked_articles = sorted(
        scored_articles, 
        key=lambda x: x.get("article_score", {}).get("final_custom_score", 0), 
        reverse=True
    )

    return reranked_articles[:top_m]