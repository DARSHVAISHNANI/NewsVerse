import numpy as np
import json
import re  # Import the regular expression module
from google.api_core.exceptions import ResourceExhausted
from Recommendation_Engine import db_manager
from Recommendation_Engine.agents import get_article_match_agent
from api_manager import api_manager

def parseJsonOutput(text: str):
    """
    Safely parses a JSON string, cleaning it of markdown artifacts and other text.
    """
    if not isinstance(text, str):
        # If the whole RunOutput object was passed by mistake, extract the content
        if hasattr(text, 'content'):
            text = text.content
        else:
            print(f"⚠️  Invalid input to parser: Expected string but got {type(text)}")
            return None
            
    try:
        # Use regex to find the JSON block, even with leading/trailing text
        json_match = re.search(r'```json\n([\s\S]*?)\n```', text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback for cases where there are no markdown fences
            json_str = text[text.find('['):text.rfind(']')+1]

        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"⚠️  Could not decode JSON from response. Error: {e}. Response text: {text}")
        return None

def rerank_articles_with_llm(user_summary: str, candidate_articles: list, top_n: int = 10):
    """ Re-ranks articles using the LLM, with API fallback. """
    print(f"🤖 Re-ranking {len(candidate_articles)} articles with LLM...")
    articles_for_prompt = [{"_id": str(a["_id"]), "title": a["title"]} for a in candidate_articles]
    prompt_input = f"User Preference Summary:\n{user_summary}\n\nShortlisted Articles:\n{json.dumps(articles_for_prompt, indent=2)}"
    ranked_ids = None

    for _ in range(2): # Max 2 retries (Gemini -> Groq)
        try:
            article_match_agent = get_article_match_agent()
            response = article_match_agent.run(prompt_input)
            
            # ------------------- THE FIX IS HERE -------------------
            # Pass the .content attribute to the parser, not the whole object
            ranked_ids = parseJsonOutput(response.content)
            # -------------------------------------------------------

            break
        except ResourceExhausted:
            print("🚨 Gemini API rate limit exceeded. Switching to Groq for ranking...")
            api_manager.switch_to_groq()
        except Exception as e:
            print(f"An unexpected error during article ranking: {e}")
            break
            
    if not ranked_ids or not isinstance(ranked_ids, list):
        print("⚠️ LLM failed to rank. Using original similarity ranking.")
        return candidate_articles[:top_n]

    # Extract article IDs from the ranked list
    # Handle both formats: list of strings ["id1", "id2"] or list of dicts [{"_id": "id1"}, ...]
    extracted_ids = []
    for item in ranked_ids:
        if isinstance(item, str):
            # Already a string ID
            extracted_ids.append(item)
        elif isinstance(item, dict):
            # Extract ID from dictionary - try common key names
            article_id = item.get("_id") or item.get("id") or item.get("article_id")
            if article_id:
                extracted_ids.append(str(article_id))
        else:
            # Convert other types to string
            extracted_ids.append(str(item))

    article_map = {str(a["_id"]): a for a in candidate_articles}
    return [article_map[article_id] for article_id in extracted_ids if article_id in article_map][:top_n]
    
def suggestArticlesForUser(summary_embedding, all_articles: list, top_n: int = 20):
    """ Suggests top N articles using embeddings as an initial filter. """
    for article in all_articles:
        article_embedding = np.array(article["embedding"], dtype=np.float32)
        sim = np.dot(summary_embedding, article_embedding) / (np.linalg.norm(summary_embedding) * np.linalg.norm(article_embedding))
        article["similarity"] = float(sim)
    return sorted(all_articles, key=lambda x: x["similarity"], reverse=True)[:top_n]

def recommendForAllUsers(user_analysis_collection, news_collection, embedding_model):
    """ Loops through all users and generates article recommendations. """
    users = db_manager.fetchAllUsersForRecommendation(user_analysis_collection)
    all_articles = db_manager.fetchAllArticlesWithEmbeddings(news_collection)
    if not all_articles:
        print("⚠️ No articles with embeddings found.")
        return

    all_recommendations = []
    for user in users:
        print(f"\n🔍 Generating recommendations for user: {user.get('name', 'Unknown')}")
        summary_embedding = embedding_model.encode(user["detailed_summary"])
        candidate_articles = suggestArticlesForUser(summary_embedding, all_articles, top_n=20)
        final_articles = rerank_articles_with_llm(user["detailed_summary"], candidate_articles, top_n=10)

        if final_articles:
            formatted_articles = [{"_id": str(a["_id"]), "title": a["title"], "similarity": round(a.get("similarity", 0), 4)} for a in final_articles]
            all_recommendations.append({"email": user["email"], "name": user.get("name"), "articles": formatted_articles})
            print(f"✅ Top {len(formatted_articles)} recommendations generated.")
        else:
            print(f"⚠️ No recommendations found.")

    return all_recommendations