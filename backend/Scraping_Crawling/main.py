# main.py

import asyncio
import json
import requests
import logging # New Import

# Import from our modules
from Scraping_Crawling import config
from Scraping_Crawling import db_manager
from Scraping_Crawling import scraper
from Scraping_Crawling.utils import IsValidArticle
import os

# --- Logging Setup ---
logger = logging.getLogger("ScrapingPipeline")
logger.setLevel(logging.INFO)


async def main():
    """Main execution function."""
    logger.info("Starting article discovery process...") # Replaced print
    
    try:
        articles_to_process = await scraper.DiscoverAllArticles()
    except Exception as e:
        logger.error(f"FATAL: Article discovery failed. Error: {e}", exc_info=True)
        return

    if not articles_to_process:
        logger.info("No articles found. Exiting.") # Replaced print
        return

    # Limit the total number of articles to 5
    articles_to_process = articles_to_process[:10]

    logger.info(f"Discovered {len(articles_to_process)} article URLs to process.") # Replaced print

    logger.info("Processing articles and extracting content...") # Replaced print
    processed_articles = []
    with requests.Session() as session:
        for i, item in enumerate(articles_to_process):
            article_url = item.get('url', 'N/A')
            logger.info(f"Processing article {i+1}/{len(articles_to_process)}: {article_url}") # Replaced print
            
            try:
                data = scraper.ProcessArticle(item, session)
            except Exception as e:
                logger.error(f"Error processing article {article_url}: {e}", exc_info=True)
                data = None

            if data and IsValidArticle(data):
                processed_articles.append(data)
                logger.info("Success: Article processed and validated.") # Replaced print
            else:
                logger.warning("Skipped: Article data was incomplete or invalid.") # Replaced print

    logger.info("-" * 50)
    logger.info(f"Successfully processed and validated {len(processed_articles)} articles.") # Replaced print

    # Save to local file
    try:
        with open(config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(processed_articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to local file: {config.OUTPUT_FILE}") # Replaced print
    except Exception as e:
        logger.error(f"Failed to save results to local file {config.OUTPUT_FILE}: {e}", exc_info=True)

    # Save to MongoDB Atlas
    logger.info("Saving articles to MongoDB Atlas...") # Replaced print
    if db_manager.SaveToMongoDB(processed_articles):
        logger.info("MongoDB storage completed successfully!") # Replaced print
        # Assuming GetMongoDBStats might print, wrapping/replacing it if necessary is done outside this file.
        # Keeping the call to maintain structure, but assuming any prints inside are now loggers.
        db_manager.GetMongoDBStats()
    else:
        logger.error("MongoDB storage failed.") # Replaced print

    logger.info("News crawling and storage process completed!") # Replaced print


if __name__ == "__main__":
    try:
        # To run the script, you execute this file from your terminal: python main.py
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unhandled exception during asyncio run: {e}", exc_info=True)