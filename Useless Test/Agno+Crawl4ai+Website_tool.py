from agno.tools.website import WebsiteTools
from datetime import datetime
import requests
import json
website_tool = WebsiteTools()

def fetch_space_news(limit=3):
    url = f"https://api.spaceflightnewsapi.net/v4/articles/?limit={limit}"
    response = requests.get(url)
    articles = []
    if response.ok:
        for a in response.json()["results"]:
            dt = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
            article_url = a["url"]
            
            # Scrape article content using WebsiteTools
            try:
                result_json = website_tool.read_url(article_url)
                documents = json.loads(result_json)
                if documents:
                    long_section = max(documents, key=lambda d: len(d.get("text", "")))
                    full_description = long_section.get("text", "").strip()
                else:
                    full_description = "No content extracted."
            except Exception as e:
                full_description = f"Error: {e}"

            articles.append({
                "title": a["title"],
                "summary": a["summary"],
                "url": article_url,
                "source": a["news_site"],
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "full_description": full_description
            })
    return articles

if __name__ == "__main__":
    articles = fetch_space_news(limit=3)

    for idx, article in enumerate(articles, 1):
        print(f"\n🛰️ Article {idx}")
        print(f"Title       : {article['title']}")
        print(f"Date & Time : {article['date']} at {article['time']}")
        print(f"Source      : {article['source']}")
        print(f"URL         : {article['url']}")
        print(f"Summary     : {article['summary']}\n")
        print(f"Full Description (trimmed):\n{article['full_description'][:1000]}")
        print("—" * 80)