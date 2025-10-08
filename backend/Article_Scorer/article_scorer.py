# backend/Article_Scorer/run_scoring.py

from google.api_core.exceptions import ResourceExhausted
from Article_Scorer import db_manager
from Article_Scorer.agents import get_scoring_agent # Import the agent creator function
from Article_Scorer.utils import parseScoreJson, saveResultsToJson
from api_manager import api_manager # Import the manager

def get_llm_score(article_text):
    """
    Gets a score from the LLM, handling API rate limits by falling back to Groq.
    """
    max_retries = 2 # Attempt 1: Gemini, Attempt 2: Groq
    for attempt in range(max_retries):
        try:
            # Get a fresh agent instance with the current model
            scoring_agent = get_scoring_agent()
            response = scoring_agent.run(article_text)
            return parseScoreJson(response)
        
        except ResourceExhausted:
            print("🚨 Gemini API rate limit exceeded. Switching to Groq for scoring...")
            api_manager.switch_to_groq()
            # The loop will automatically retry with the new Groq model
            
        except Exception as e:
            print(f"An unexpected error occurred while scoring: {e}")
            # For other errors, we break the loop to avoid repeated failures
            return None
    
    print("❌ Failed to get a score after exhausting all available models.")
    return None


def main():
    """Main function to run the article scoring process."""

    # 1. Connect and fetch articles
    collection = db_manager.connectToDb()
    if collection is None:
        return

    articles = db_manager.fetchAllArticles(collection)
    if not articles:
        return

    # 2. Group articles by title to handle duplicates
    articles_by_title = {}
    for art in articles:
        title = art.get("title", "").strip().lower()
        if title:
            if title not in articles_by_title:
                articles_by_title[title] = []
            articles_by_title[title].append(art)

    results_list = []

    # 3. Process each group of articles
    for title, docs in articles_by_title.items():
        representative_doc = docs[0]  # Use one article for LLM scoring

        # --- Get user score if it exists ---
        user_score = None
        for doc in docs:
            if doc.get("article_score", {}).get("user_article_score") is not None:
                user_score = doc["article_score"]["user_article_score"]
                break

        # --- Get a fresh LLM score using the new robust function ---
        article_text = f"{representative_doc.get('title', '')}\n\n{representative_doc.get('content', '')}"
        score_data = get_llm_score(article_text) # <<< INTEGRATION POINT

        if not score_data:
            print(f"❌ Skipping article group '{title}' due to invalid LLM response.")
            continue

        llm_score = int(score_data.get("score", 0))
        reason = score_data.get("reason", "No reason provided.")

        # --- Compute final score ---
        final_score = round((llm_score * 0.6) + (user_score * 0.4), 2) if user_score is not None else llm_score

        # 4. Update all articles in the group
        score_payload = {
            "user_article_score": user_score,
            "llm_score": llm_score,
            "final_custom_score": final_score
        }
        for doc in docs:
            db_manager.updateArticleScores(collection, doc["_id"], score_payload)

        # 5. Add to our list for local file saving
        results_list.append({
            "title": title.capitalize(),
            "user_article_score": user_score,
            "llm_score": llm_score,
            "final_custom_score": final_score,
            "score_reason": reason
        })

    # 6. Save all results to a local JSON file
    saveResultsToJson(results_list, "article_scores.json")
    print("\n🎉 Article scoring process complete!")

if __name__ == "__main__":
    main()