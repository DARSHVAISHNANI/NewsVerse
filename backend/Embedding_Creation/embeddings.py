from Embedding_Creation import db_manager
from Embedding_Creation.model_loader import embedding_model

def storeArticleEmbeddings():
    """
    Main function to generate and store embeddings for articles.
    """
    # 1. Connect to the database and get the collection
    collection = db_manager.connectToDb()
    if collection is None:
        return

    # 2. Fetch only the articles that need an embedding
    articles_to_process = db_manager.fetchArticlesWithoutEmbeddings(collection)

    if not articles_to_process:
        print("✅ All articles already have embeddings. Nothing to do.")
        return

    # 3. Process each article
    count = 0
    for article in articles_to_process:
        # Combine title and content for a richer embedding
        text_to_embed = f"{article.get('title', '')} {article.get('content', '')}"

        # 4. Generate the embedding using the pre-loaded model
        embedding = embedding_model.encode(text_to_embed).tolist()

        # 5. Update the article in the database
        db_manager.updateArticleEmbedding(collection, article["_id"], embedding)
        count += 1
        print(f"  -> Embedded article {count}/{len(articles_to_process)}")

    print(f"\n✅ Embeddings stored for {count} new articles.")


if __name__ == "__main__":
    storeArticleEmbeddings()