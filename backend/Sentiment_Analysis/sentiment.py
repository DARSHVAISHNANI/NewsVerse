import json
from google.api_core.exceptions import ResourceExhausted

# Import from our new modules
from Sentiment_Analysis import db_manager
from Sentiment_Analysis.agents import get_sentiment_agent # Import the agent creator
from Sentiment_Analysis.utils import CleanJsonOutput
from api_manager import api_manager # Import the manager

def main():
    """
    Main function to run the sentiment analysis process.
    """
    # 1. Connect to the database
    collection = db_manager.ConnectToMongoDB()
    if collection is None:
        print("Exiting: Database connection failed.")
        return

    # 2. Fetch articles that need sentiment analysis
    articles = db_manager.FetchArticlesToAnalyzeSentiment(collection)
    if not articles:
        print("No new articles to analyze for sentiment. All done!")
        return

    json_results = []

    # 3. Process each article
    for article in articles:
        content = article.get("content", "")
        if not content or not content.strip():
            print(f"⏩ Skipping article '{article.get('title', 'N/A')}' due to empty content.")
            continue

        print("\n" + "="*80)
        print(f"Processing Article: {article.get('title', 'N/A')}")

        sentiment_data = None
        
        # --- Integration of API fallback logic ---
        max_retries = 2  # Attempt 1: Gemini, Attempt 2: Groq
        for attempt in range(max_retries):
            try:
                # Get a fresh agent instance with the current model
                sentiment_agent = get_sentiment_agent()
                response = sentiment_agent.generate_response(content)
                cleaned_text = CleanJsonOutput(response)
                sentiment_data = json.loads(cleaned_text)
                print(f"   ✓ Sentiment: Generated")
                break # If successful, exit the retry loop
            except ResourceExhausted:
                print("🚨 Gemini API rate limit exceeded. Switching to Groq for sentiment analysis...")
                api_manager.switch_to_groq()
                # The loop will automatically retry with the new Groq model
            except Exception as e:
                print(f"   ✗ Sentiment: Failed ({e})")
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
            print(f"   💾 Database updated.")

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
        print(f"\n✅ Saved {len(json_results)} sentiment results to '{filename}'")

    print("\n🎉 Sentiment analysis process complete!")

if __name__ == "__main__":
    main()