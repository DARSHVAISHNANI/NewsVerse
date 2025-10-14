from Embedding_Creation import db_manager
from Embedding_Creation.model_loader import embedding_model
import logging # New Import

# --- Logging Setup ---
logger = logging.getLogger("EmbeddingCreationPipeline")
logger.setLevel(logging.INFO)


def storeArticleEmbeddings():
    """
    Main function to generate and store embeddings for articles.
    """
    # 1. Connect to the database and get the collection
    collection = db_manager.connectToDb()
    if collection is None:
        logger.critical("Exiting: Database connection failed.") # Added logger for connection failure
        return

    # 2. Fetch only the articles that need an embedding
    articles_to_process = db_manager.fetchArticlesWithoutEmbeddings(collection)

    if not articles_to_process:
        logger.info("All articles already have embeddings. Nothing to do.") # Replaced print
        return

    # 3. Process each article
    count = 0
    total_articles = len(articles_to_process)
    logger.info(f"Starting to process {total_articles} articles for embedding.") # Added logger
    
    for article in articles_to_process:
        try:
            # Combine title and content for a richer embedding
            text_to_embed = f"{article.get('title', '')} {article.get('content', '')}"

            # 4. Generate the embedding using the pre-loaded model
            embedding = embedding_model.encode(text_to_embed).tolist()

            # 5. Update the article in the database
            db_manager.updateArticleEmbedding(collection, article["_id"], embedding)
            count += 1
            logger.debug(f"Embedded article {count}/{total_articles}") # Replaced print with debug/info

        except Exception as e:
            logger.error(f"Failed to generate/store embedding for article {article.get('_id', 'N/A')}. Error: {e}", exc_info=True)
            # Continue to the next article

    logger.info(f"Embeddings stored for {count} new articles.") # Replaced print


if __name__ == "__main__":
    storeArticleEmbeddings()