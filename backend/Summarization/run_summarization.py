import json
from google.api_core.exceptions import ResourceExhausted
import logging

from Summarization import db_manager
from Summarization.agents import get_summarization_agent, get_story_agent
from Summarization.utils import CleanJsonOutput
from api_manager import api_manager

logger = logging.getLogger("SummarizationPipeline")
logger.setLevel(logging.INFO)


def get_factual_summary(content):
    """Gets a factual summary, handling API fallbacks."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            summarization_agent = get_summarization_agent()
            response = summarization_agent.run(content)
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            cleaned_text = CleanJsonOutput(response_content)
            summary_data = json.loads(cleaned_text)
            return summary_data.get("summary", "")
        except ResourceExhausted:
            logger.warning("Gemini API rate limit exceeded for factual summary. Switching to Groq...")
            api_manager.switch_to_groq()
        except Exception as e:
            error_msg = f"'{type(response).__name__}' object has no attribute 'strip'" if 'strip' in str(e) and 'response' in locals() else e
            logger.error(f"Factual Summary: Failed. Error: {error_msg}", exc_info=True)
            return ""
    logger.error("Failed to get factual summary after exhausting all models.")
    return ""

def get_story_summary(content):
    """Gets a story summary, handling API fallbacks."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            story_agent = get_story_agent()
            story_response = story_agent.run(content)
            
            story_response_content = story_response.content if hasattr(story_response, 'content') else str(story_response)
            
            story_cleaned = CleanJsonOutput(story_response_content)
            story_data = json.loads(story_cleaned)
            return story_data.get("story_summary", "")
        except ResourceExhausted:
            logger.warning("Gemini API rate limit exceeded for story summary. Switching to Groq...")
            api_manager.switch_to_groq()
        except Exception as e:
            error_msg = f"'{type(story_response).__name__}' object has no attribute 'strip'" if 'strip' in str(e) and 'story_response' in locals() else e
            logger.error(f"Story Summary: Failed. Error: {error_msg}", exc_info=True)
            return ""
    logger.error("Failed to get story summary after exhausting all models.")
    return ""


def main():
    """
    Main function to run the summarization process.
    """
    # 1. Connect to the database
    collection = db_manager.ConnectToMongoDB()
    if collection is None:
        logger.critical("Exiting: Database connection failed.")
        return

    # 2. Fetch articles that need summaries
    articles = db_manager.FetchArticlesToSummarize(collection)
    if not articles:
        logger.info("No new articles to summarize. All done!")
        return

    # 3. Process each article
    for article in articles:
        content = article.get("content", "")
        if not content or not content.strip():
            logger.warning(f"Skipping article '{article.get('title', 'N/A')}' due to empty content.")
            continue

        logger.info("="*80)
        logger.info(f"Processing Article: {article.get('title', 'N/A')}")

        summary_text = get_factual_summary(content)
        if summary_text:
            logger.info("Factual Summary: Generated")

        story_text = get_story_summary(content)
        if story_text:
            logger.info("Story Summary: Generated")

        # 4. Update the article in the database
        if summary_text or story_text:
            db_manager.UpdateArticleSummaries(
                collection,
                article["_id"],
                summary_text,
                story_text
            )
            logger.info("Database updated.")

    logger.info("Summarization process complete!")

if __name__ == "__main__":
    main()