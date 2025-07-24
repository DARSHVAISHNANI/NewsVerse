from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.website import WebsiteTools
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Utility: Fetch latest space news
# -----------------------------
def fetch_space_news(limit=3):
    url = f"https://api.spaceflightnewsapi.net/v4/articles/?limit={limit}"
    response = requests.get(url)
    articles = []
    if response.ok:
        for a in response.json()["results"]:
            dt = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
            articles.append({
                "title": a["title"],
                "summary": a["summary"],
                "url": a["url"],
                "source": a["news_site"],
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M")
            })
    return articles

# -----------------------------
# Agent 1: Display latest headlines from API
# -----------------------------
space_news_agent = Agent(
    name="SpaceflightNewsAgent",
    model=Groq(id="qwen/qwen3-32b"),
    description="Fetches latest headlines from the Spaceflight News API.",
    instructions=[
        "Call the fetch_space_news function.",
        "Return each article’s title, summary, source, date, time, and URL."
    ],
    markdown=True,
    show_tool_calls=False
)

# -----------------------------
# Agent 2: Extract article content using WebsiteTool
# -----------------------------
space_article_extractor = WebsiteTools()

# -----------------------------
# Format + Print final structured articles
# -----------------------------
articles = fetch_space_news(limit=2)

for article in articles:
    print(f"\n\n### 🛰️ {article['title']}")
    print(f"**Published**: {article['date']} at {article['time']} — *{article['source']}*")
    print(f"🔗 [URL]({article['url']})")
    print(f"🔎 Summary: {article['summary']}\n")

    # Use WebsiteTool directly to extract the full article
    content = space_article_extractor.run(article["url"])

    # Print structured output
    print(f"---\n**📝 Structured Article:**\n")
    print(f"- title: {article['title']}")
    print(f"- full_description: {content[:2000]}")  # optional truncate for console safety
    print(f"- url: {article['url']}")
    print(f"- date: {article['date']}")
    print(f"- time: {article['time']}")