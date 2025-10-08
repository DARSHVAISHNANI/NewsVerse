# main.py

import asyncio
import json

import requests

# Import from our modules
from Scraping_Crawling import config
from Scraping_Crawling import db_manager
from Scraping_Crawling import scraper
from Scraping_Crawling.utils import IsValidArticle
import asyncio, os

async def main():
    """Main execution function."""
    print("🚀 Starting article discovery process...")
    articles_to_process = await scraper.DiscoverAllArticles()

    if not articles_to_process:
        print("\n❌ No articles found. Exiting.")
        return

    # Limit the total number of articles to 5
    articles_to_process = articles_to_process[:20]

    print(f"\n✅ Discovered {len(articles_to_process)} article URLs to process.")

    print("\n📖 Processing articles and extracting content...")
    processed_articles = []
    with requests.Session() as session:
        for i, item in enumerate(articles_to_process):
            print(f"Processing article {i+1}/{len(articles_to_process)}: {item['url']}")
            data = scraper.ProcessArticle(item, session)

            if data and IsValidArticle(data):
                processed_articles.append(data)
                print("   -> Success: Article processed and validated.")
            else:
                print("   -> Skipped: Article data was incomplete or invalid.")

    print("-" * 50)
    print(f"Successfully processed and validated {len(processed_articles)} articles.")

    # Save to local file
    with open(config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_articles, f, indent=2, ensure_ascii=False)
    print(f"📁 Results saved to local file: {config.OUTPUT_FILE}")

    # Save to MongoDB Atlas
    print("\n🗄️  Saving articles to MongoDB Atlas...")
    if db_manager.SaveToMongoDB(processed_articles):
        print("✅ MongoDB storage completed successfully!")
        db_manager.GetMongoDBStats()
    else:
        print("❌ MongoDB storage failed.")

    print("\n🎉 News crawling and storage process completed!")


if __name__ == "__main__":
    # To run the script, you execute this file from your terminal: python main.py
    asyncio.run(main())