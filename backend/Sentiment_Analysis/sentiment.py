import json
from google.api_core.exceptions import ResourceExhausted
import logging # New Import

# Import from our new modules
from Sentiment_Analysis import db_manager
from Sentiment_Analysis.agents import get_sentiment_agent # Import the agent creator
from Sentiment_Analysis.utils import CleanJsonOutput
from api_manager import api_manager # Import the manager

# --- Logging Setup ---
logger = logging.getLogger("SentimentAnalysis")
logger.setLevel(logging.INFO)


def main():
    """
    Main function to run the sentiment analysis process.
    """
    # 1. Connect to the database
    collection = db_manager.ConnectToMongoDB()
    if collection is None:
        logger.critical("Exiting: Database connection failed.") # Replaced print
        return

    # 2. Fetch articles that need sentiment analysis
    articles = db_manager.FetchArticlesToAnalyzeSentiment(collection)
    if not articles:
        logger.info("No new articles to analyze for sentiment. All done!") # Replaced print
        return

    json_results = []

    # 3. Process each article
    for article in articles:
        content = article.get("content", "")
        if not content or not content.strip():
            logger.warning(f"Skipping article '{article.get('title', 'N/A')}' due to empty content.") # Replaced print
            continue

        logger.info("="*80) # Replaced print
        logger.info(f"Processing Article: {article.get('title', 'N/A')}") # Replaced print

        sentiment_data = None
        
        # --- Integration of API fallback logic ---
        max_retries = 2  # Attempt 1: Gemini, Attempt 2: Groq
        for attempt in range(max_retries):
            response = None # Initialize response for logging outside the try block
            try:
                # Get a fresh agent instance with the current model
                sentiment_agent = get_sentiment_agent()
                response = sentiment_agent.run(content)
                
                # --- FIX: Extract content from the agno RunOutput object ---
                response_content = response.content if hasattr(response, 'content') else str(response)

                cleaned_text = CleanJsonOutput(response_content)
                sentiment_data = json.loads(cleaned_text)
                logger.info("Sentiment: Generated") # Replaced print
                break # If successful, exit the retry loop
            except ResourceExhausted:
                logger.warning("Gemini API rate limit exceeded. Switching to Groq for sentiment analysis...") # Replaced print
                api_manager.switch_to_groq()
                # The loop will automatically retry with the new Groq model
            except Exception as e:
                # Added type check for better logging
                error_msg = f"'{type(response).__name__}' object has no attribute 'strip'" if 'strip' in str(e) and response is not None else e
                logger.error(f"Sentiment: Failed. Error: {error_msg}", exc_info=True) # Replaced print
                break # For other errors, exit the loop
        # --- End of integration ---
        
        sentiment_text = sentiment_data.get("sentiment", "") if sentiment_data else ""

        # 4. Update the article in the database
        if sentiment_text:
            db_manager.UpdateArticleSentiment(
                collection,
                article["_id"],
                sentiment_text
            )
            logger.info("Database updated.") # Replaced print

        # Append to our local JSON file results
        json_results.append({
            "article_id": str(article["_id"]),
            "title": article.get("title"),
            "sentiment": sentiment_text,
        })

    # 5. Save all results to a local file
    if json_results:
        filename = "sentiment_analysis.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(json_results)} sentiment results to '{filename}'") # Replaced print

    logger.info("Sentiment analysis process complete!") # Replaced print

if __name__ == "__main__":
    main()