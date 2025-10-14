from google.api_core.exceptions import ResourceExhausted
import logging # New Import
from Name_Entity_Recognition import db_manager
from Name_Entity_Recognition.agents import get_ner_agent # Import the agent creator
from Name_Entity_Recognition.utils import parseJsonOutput
from api_manager import api_manager # Import the manager

# --- Logging Setup ---
logger = logging.getLogger("NERPipeline")
logger.setLevel(logging.INFO)


def get_ner_from_llm(article_text):
    """
    Gets NER data from the LLM, handling API rate limits by falling back to Groq.
    """
    max_retries = 2  # Attempt 1: Gemini, Attempt 2: Groq
    for attempt in range(max_retries):
        try:
            # Get a fresh agent instance with the current model
            ner_agent = get_ner_agent()
            response = ner_agent.run(article_text)
            return parseJsonOutput(response)
            
        except ResourceExhausted:
            logger.warning("Gemini API rate limit exceeded. Switching to Groq for NER processing...") # Replaced print
            api_manager.switch_to_groq()
            # The loop will automatically retry with the new Groq model
            
        except Exception as e:
            logger.error(f"An unexpected error occurred during NER processing: {e}", exc_info=True) # Replaced print
            return None
            
    logger.error("Failed to get NER data after exhausting all available models.") # Replaced print
    return None

def runNerForUsers():
    """Main function to run the NER process for all users."""

    news_collection, user_collection = db_manager.connectToDbs()
    if news_collection is None or user_collection is None:
        logger.critical("Exiting NER: Database connection failed.") # Added logger
        return

    all_users = db_manager.fetchAllUsers(user_collection)

    for user in all_users:
        user_name = user.get("name")
        title_ids = user.get("title_id_list", [])
        logger.info(f"Processing NER for user: '{user_name}'...") # Replaced print

        aggregated_ner = {"Person": set(), "Location": set(), "Organization": set()}

        for article_id in title_ids:
            article = db_manager.fetchArticleById(news_collection, article_id)
            if not article or not article.get("content"):
                logger.warning(f"Article {article_id} missing or has no content, skipping.") # Replaced print
                continue

            # Get NER data using the new robust function
            ner_json = get_ner_from_llm(article["content"]) # <<< INTEGRATION POINT

            if ner_json:
                for entity_type in aggregated_ner:
                    entities = ner_json.get(entity_type, [])
                    if isinstance(entities, list):
                        aggregated_ner[entity_type].update(e.strip() for e in entities if isinstance(e, str))

        final_ner_doc = {k: sorted(list(v)) for k, v in aggregated_ner.items()}

        db_manager.updateUserNer(user_collection, user["_id"], final_ner_doc)
        logger.info(f"Updated NER for user '{user_name}'") # Replaced print

    logger.info("NER processing complete for all users!") # Replaced print


if __name__ == "__main__":
    runNerForUsers()