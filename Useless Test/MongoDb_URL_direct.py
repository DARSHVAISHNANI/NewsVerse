import re
import json
import certifi
import requests
from agno.agent import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools
from agno.tools.crawl4ai import Crawl4aiTools
from typing import Optional

load_dotenv()

class ArticleInfo(BaseModel):
    title: str
    url: Optional[str]
    topic_category: str

# MongoDB connection
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())
db = client["NewsVerseDB"]
collection = db["NewsVerseCo"]

# Step 0: Extract all article titles from DB
titles = [doc.get("title") for doc in collection.find({}, {"title": 1, "_id": 0}) if doc.get("title")]
if not titles:
    raise ValueError("No titles found in the collection.")

# Step 1: Analyze dominant topic/category and themes using LLM agent
pattern_analyzer_agent = Agent(
    name="PatternAnalyzerAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You are a text analysis expert. Analyze the following list of article titles and identify the dominant topic/theme patterns.\n"
        "Determine what category these articles predominantly belong to (e.g., Technology, Sports, Politics, Business, Health, Entertainment, etc.).\n"
        "Also identify key keywords and themes that appear frequently.\n"
        "Reply with a JSON object containing:\n"
        "- 'dominant_category': one of ['Technology', 'Sports', 'Politics', 'Business', 'Health', 'Entertainment']\n"
        "- 'key_themes': list of 3-5 main themes/topics\n"
        "- 'keywords': list of 5-10 most relevant keywords\n"
        "Example: {\"dominant_category\": \"Technology\", \"key_themes\": [\"AI\", \"Software\", \"Innovation\"], "
        "\"keywords\": [\"tech\", \"AI\", \"software\", \"innovation\", \"digital\"]}\n\n"
        "Titles to analyze:\n" + "\n".join(titles)
    ),
    tools=[DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)

pattern_result = pattern_analyzer_agent.run("Analyze the topic patterns in the given titles.")
pattern_content = pattern_result.content.strip()

try:
    pattern_data = json.loads(pattern_content)
    dominant_category = pattern_data.get("dominant_category")
    # Validate dominant_category presence and type
    if not dominant_category or not isinstance(dominant_category, str):
        raise ValueError("Dominant category missing or invalid")
    dominant_category = dominant_category.strip().title()
    key_themes = pattern_data.get("key_themes", [])
    keywords = pattern_data.get("keywords", [])
except Exception as e:
    print(f"[Warning] Pattern analysis failed ({e}), using fallback method.")
    all_text = " ".join(titles).lower()
    tech_keywords = ["technology", "tech", "ai", "software", "digital", "data", "computer", "innovation", "startup", "app"]
    business_keywords = ["business", "company", "market", "economy", "finance", "stock", "investment", "corporate"]
    sports_keywords = ["sport", "game", "player", "team", "match", "championship", "league", "tournament"]
    health_keywords = ["health", "medical", "covid", "disease", "vaccine", "hospital"]
    entertainment_keywords = ["entertainment", "movie", "film", "music", "celebrity", "tv"]

    counts = {
        'Technology': sum(all_text.count(k) for k in tech_keywords),
        'Business': sum(all_text.count(k) for k in business_keywords),
        'Sports': sum(all_text.count(k) for k in sports_keywords),
        'Health': sum(all_text.count(k) for k in health_keywords),
        'Entertainment': sum(all_text.count(k) for k in entertainment_keywords)
    }

    dominant_category = max(counts, key=counts.get)
    
    cat_to_keywords = {
        'Technology': tech_keywords,
        'Business': business_keywords,
        'Sports': sports_keywords,
        'Health': health_keywords,
        'Entertainment': entertainment_keywords
    }
    keywords = cat_to_keywords.get(dominant_category, [])
    key_themes = keywords[:3]

print(f"Detected dominant category: {dominant_category}")
print(f"Key themes: {key_themes}")
print(f"Keywords: {keywords}")

# Step 2: Map dominant category to a news site section URL
def get_news_site_url(category: str) -> str:
    cat = category.lower()
    if cat == 'technology':
        return "https://www.bbc.com/news/innovation"
    elif cat == 'sports':
        return "https://www.bbc.com/sport"
    elif cat == 'business':
        return "https://www.bbc.com/news/business"
    elif cat == 'health':
        return "https://www.bbc.com/news/health"
    elif cat == 'entertainment':
        return "https://www.bbc.com/news/entertainment_and_arts"
    else:
        return "https://www.bbc.com/news"

news_site_url = get_news_site_url(dominant_category)


crawl_agent = Agent(
    name="NewsSiteCrawlerAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        f"Your goal is to crawl the news site at '{news_site_url}' and extract a recent article.\n"
        "Specifically, look for HTML anchor (`<a>`) tags that satisfy the following conditions:\n"
        "- The tag has an href attribute starting with '/news/articles/' **AND**\n"
        "- The tag has the attribute `data-testid=\"internal-link\"`\n"
        "Extract the href value (the relative URL path) from such tags.\n"
        "Construct the full article URL by prefixing the base URL 'https://www.bbc.com' with the extracted href.\n"
        "Verify the full URL is live and not broken or paywalled.\n"
        "Return ONLY a JSON object with the article's title, the full URL, and the topic_category.\n"
        "Use Crawl4aiTools primarily to crawl the page, and fallback on DuckDuckGoTools and WebBrowserTools if necessary.\n"
        "Never return incomplete URLs or URLs not matching the specified tag and attribute pattern.\n"
    ),
    tools=[Crawl4aiTools(), DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
    response_model=ArticleInfo
)


result = crawl_agent.run(f"Crawl and extract article URL and title from '{news_site_url}' focused on '{dominant_category}'.")

print("\n=== RESULTS ===")
print(f"Dominant Category: {dominant_category}")
print(f"News Site URL: {news_site_url}")
print(f"Extracted Article Title: {result.content.title}")
print(f"Extracted Article URL: {result.content.url}")