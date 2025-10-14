import json
from google.api_core.exceptions import ResourceExhausted
import logging # New Import

# Import from our new modules
from Fact_Checker import db_manager
from Fact_Checker.agents import get_fact_checker_agent # Import the agent creator
from Fact_Checker.utils import parseJsonOutput
from api_manager import api_manager # Import the manager

# --- Logging Setup ---
logger = logging.getLogger("FactCheckerPipeline")
logger.setLevel(logging.INFO)


def get_fact_check_from_llm(article_text):
    """
    Gets a fact-check result from the LLM, handling API rate limits by falling back to Groq.
    """
    max_retries = 2  # Attempt 1: Gemini, Attempt 2: Groq
    for attempt in range(max_retries):
        try:
            # Get a fresh agent instance with the current model
            fact_checker_agent = get_fact_checker_agent()
            response = fact_checker_agent.run(article_text)

            # --- THIS IS THE FIX ---
            # Extract the 'content' attribute from the RunOutput object
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                # Fallback for other cases
                response_content = str(response)

            return parseJsonOutput(response_content)

        except ResourceExhausted:
            logger.warning("Gemini API rate limit exceeded. Switching to Groq for fact-checking...") # Replaced print
            api_manager.switch_to_groq()
            # The loop will automatically retry with the new Groq model

        except Exception as e:
            logger.error(f"An unexpected error occurred during fact-checking: {e}", exc_info=True) # Replaced print
            return None

    logger.error("Failed to get a fact-check result after exhausting all available models.") # Replaced print
    return None


def main():
    """Main function to run the fact-checking process."""

    # 1. Connect to DB and fetch articles
    collection = db_manager.connectToDb()
    if collection is None:
        logger.critical("Exiting: Database connection failed.") # Added logger
        return

    articles = db_manager.fetchAllArticles(collection)

    # Use a dummy article for testing if the DB is empty
    if not articles:
        logger.warning("No articles found in DB, using dummy article for testing.") # Replaced print
        articles = [{"_id": "dummy1", "content": "Apple Inc. reported record revenue of $120 billion in Q4 2024."}]

    results = []

    # 2. Process each article
    for article in articles:
        article_id = str(article["_id"])
        article_text = article.get("content", "")

        if not article_text.strip():
            logger.warning(f"Skipping article {article_id} (empty content).") # Replaced print
            continue

        logger.info(f"Fact-checking article {article_id}...") # Replaced print

        # 3. Run the agent and parse the response using the new robust function
        fact_result = get_fact_check_from_llm(article_text) # <<< INTEGRATION POINT

        if fact_result:
            results.append({
                "article_id": article_id,
                "llm_verdict": fact_result.get("llm_verdict"),
                "fact_check_explanation": fact_result.get("fact_check_explanation")
            })

            # 4. Update the database
            db_manager.updateArticleFactCheck(collection, article["_id"], fact_result, article)

            logger.info(f"Fact check result for article {article_id}: {fact_result}") # Replaced print
        else:
            logger.error(f"Failed to get a valid JSON result for article {article_id}.") # Replaced print

    # 5. Save results to a local file
    output_file = "fact_check_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    logger.info(f"Results for {len(results)} articles saved to {output_file}") # Replaced print

if __name__ == "__main__":
    main()