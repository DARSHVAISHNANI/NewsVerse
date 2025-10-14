import json
from google.api_core.exceptions import ResourceExhausted

# Import from our new modules
from Summarization import db_manager
from Summarization.agents import get_summarization_agent, get_story_agent # Import agent creators
from Summarization.utils import CleanJsonOutput
from api_manager import api_manager # Import the manager

def get_factual_summary(content):
    """Gets a factual summary, handling API fallbacks."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            summarization_agent = get_summarization_agent()
            response = summarization_agent.run(content)
            
            # --- FIX: Extract content from the agno RunOutput object ---
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            cleaned_text = CleanJsonOutput(response_content)
            summary_data = json.loads(cleaned_text)
            return summary_data.get("summary", "")
        except ResourceExhausted:
            print("🚨 Gemini API rate limit exceeded. Switching to Groq for factual summary...")
            api_manager.switch_to_groq()
        except Exception as e:
            # Added type check for better logging
            error_msg = f"'{type(response).__name__}' object has no attribute 'strip'" if 'strip' in str(e) and 'response' in locals() else e
            print(f"   ✗ Factual Summary: Failed ({error_msg})")
            return ""
    print("❌ Failed to get factual summary after exhausting all models.")
    return ""

def get_story_summary(content):
    """Gets a story summary, handling API fallbacks."""
    # Note: We don't reset the api_manager, so if it switched for the factual summary, it stays on Groq.
    max_retries = 2
    for attempt in range(max_retries):
        try:
            story_agent = get_story_agent()
            story_response = story_agent.run(content)
            
            # --- FIX: Extract content from the agno RunOutput object ---
            story_response_content = story_response.content if hasattr(story_response, 'content') else str(story_response)
            
            story_cleaned = CleanJsonOutput(story_response_content)
            story_data = json.loads(story_cleaned)
            return story_data.get("story_summary", "")
        except ResourceExhausted:
            # This will only trigger if the first call of the script is a story summary that fails
            print("🚨 Gemini API rate limit exceeded. Switching to Groq for story summary...")
            api_manager.switch_to_groq()
        except Exception as e:
            # Added type check for better logging
            error_msg = f"'{type(story_response).__name__}' object has no attribute 'strip'" if 'strip' in str(e) and 'story_response' in locals() else e
            print(f"   ✗ Story Summary: Failed ({error_msg})")
            return ""
    print("❌ Failed to get story summary after exhausting all models.")
    return ""


def main():
    """
    Main function to run the summarization process.
    """
    # 1. Connect to the database
    collection = db_manager.ConnectToMongoDB()
    if collection is None:
        print("Exiting: Database connection failed.")
        return

    # 2. Fetch articles that need summaries
    articles = db_manager.FetchArticlesToSummarize(collection)
    if not articles:
        print("No new articles to summarize. All done!")
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

        # --- Factual summarization ---
        summary_text = get_factual_summary(content)
        if summary_text:
            print(f"   ✓ Factual Summary: Generated")

        # --- Storytelling summarization ---
        story_text = get_story_summary(content)
        if story_text:
            print(f"   ✓ Story Summary: Generated")

        # 4. Update the article in the database
        if summary_text or story_text:
            db_manager.UpdateArticleSummaries(
                collection,
                article["_id"],
                summary_text,
                story_text
            )
            print(f"   💾 Database updated.")

        # Append to our local JSON file results
        json_results.append({
            "article_id": str(article["_id"]),
            "title": article.get("title"),
            "summarization": {
                "summary": summary_text,
                "story_summary": story_text
            },
        })

    # 5. Save all results to a local file
    if json_results:
        filename = "summarization_results.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(json_results)} summaries to '{filename}'")

    print("\n🎉 Summarization process complete!")

if __name__ == "__main__":
    main()