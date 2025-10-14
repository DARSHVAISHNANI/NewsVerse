# backend/Article_Scorer/article_scorer.py

from google.api_core.exceptions import ResourceExhausted
import logging # New Import
from Article_Scorer import db_manager
from Article_Scorer.agents import get_scoring_agent # Import the agent creator function
from Article_Scorer.utils import parseScoreJson, saveResultsToJson
from api_manager import api_manager # Import the manager

# --- Logging Setup ---
logger = logging.getLogger("ArticleScorerPipeline")
logger.setLevel(logging.INFO)


def get_llm_score(article_text):
    """
    Gets a score from the LLM, handling API rate limits by falling back to Groq.
    """
    max_retries = 2 # Attempt 1: Gemini, Attempt 2: Groq
    
    # Store the raw response to log if parsing fails
    last_response_content = None 
    
    for attempt in range(max_retries):
        try:
            # Get a fresh agent instance with the current model
            scoring_agent = get_scoring_agent()
            response = scoring_agent.run(article_text)
            
            # --- AGNO Response Extraction ---
            # Extract the 'content' attribute from the RunOutput object
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)
                
            last_response_content = response_content # Store the content
            
            # Attempt to parse
            parsed_data = parseScoreJson(response_content)
            
            if parsed_data:
                return parsed_data
            else:
                # If parsing fails but no exception, it returns None.
                raise ValueError("Parsing returned None.")

        except ResourceExhausted:
            logger.warning("Gemini API rate limit exceeded. Switching to Groq for scoring...") # Replaced print
            api_manager.switch_to_groq()
            # The loop will automatically retry with the new Groq model

        except Exception as e:
            # Log generic errors during run/parse
            logger.error(f"An unexpected error occurred while scoring: {e}", exc_info=True) # Replaced print
            if last_response_content:
                logger.debug(f"Raw response content on failure:\n---\n{last_response_content}\n---") # Replaced print
            # For other errors, we break the loop to avoid repeated failures
            if attempt == max_retries - 1:
                break # Break only on the final attempt
            # The loop continues to the next attempt/model otherwise
            
    logger.error("Failed to get a score after exhausting all available models.") # Replaced print
    return None


def main():
    """Main function to run the article scoring process."""

    # 1. Connect and fetch articles
    collection = db_manager.connectToDb()
    if collection is None:
        logger.critical("Exiting: Database connection failed.") # Added logger
        return

    articles = db_manager.fetchAllArticles(collection)
    if not articles:
        logger.info("No articles found to score. Exiting.") # Added logger
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
            logger.error(f"Skipping article group '{title}' due to invalid LLM response.") # Replaced print
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
    logger.info("Article scoring process complete!") # Replaced print

if __name__ == "__main__":
    main()