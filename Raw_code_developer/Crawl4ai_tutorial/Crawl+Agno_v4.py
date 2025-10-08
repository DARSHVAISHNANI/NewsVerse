import asyncio
from typing import List, Callable, Dict
from crawl4ai import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime, timedelta
from agno.agent import Agent
from dotenv import load_dotenv
from typing import List, Optional
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

parser_model = Groq(id="meta-llama/llama-4-scout-17b-16e-instruct")
groq_model = Groq(id="meta-llama/llama-4-scout-17b-16e-instruct")

class RawArticleData(BaseModel):
    """Raw, unprocessed data scraped from an article URL."""
    title: Optional[str] = Field(None, description="The raw title scraped from the page.")
    content: str = Field(..., description="The main text content scraped from the article.")
    url: str = Field(..., description="The source URL of the content.")

class FormattedArticle(BaseModel):
    """A final, structured, and formatted news article."""
    title: str = Field(..., description="The clean headline of the article.")
    full_description: str = Field(..., description="A comprehensive summary of the article (at least 200 words).")
    source: str = Field(..., description="The publisher's name (e.g., BBC, CNN).")
    date: Optional[str] = Field(None, description="The published date in YYYY-MM-DD format.")
    url: str = Field(..., description="The final, working URL of the article.")


# --------- CONFIG --------- #
DAYS_AGO = 0  # Change to 1 or 2 to allow articles from past N days
TARGET_DATE = (datetime.now() - timedelta(days=DAYS_AGO)).strftime("%Y-%m-%d")
DATE_PATTERN = TARGET_DATE[:10].replace("-", "/")  # '2025/07/23'

# -------- FILTER RULES -------- #
def url_has_target_date(href: str) -> bool:
    return DATE_PATTERN in href

def benzinga_filter(href, title):
    return "/news/" in href and title and "benzinga.com" not in title.lower()

def bbc_filter(href, title):
    return "/news/" in href and title and len(title.split()) > 2

def cnn_filter(href, title):
    return (
        any(x in href for x in ["/2025/", "/2024/"]) and
        any(x in href for x in ["/world/", "/middleeast/", "/politics/"]) and
        url_has_target_date(href) and
        title
    )

# -------- CORE LOGIC -------- #
async def extract_titles_and_urls(source_name: str, target_url: str, filter_rule: Callable[[str, str], bool]) -> List[Dict[str, str]]:
    async with AsyncWebCrawler() as crawler:
        result: CrawlResult = await crawler.arun(target_url)

    if not result.success:
        print(f"[!] Failed to crawl {target_url}")
        return []

    soup = BeautifulSoup(result.cleaned_html, "html.parser")
    articles = []

    for link in soup.find_all("a", href=True):
        href = link['href']
        title = link.get_text(strip=True)
        if filter_rule(href, title):
            full_url = urljoin(target_url, href)
            articles.append({
                "title": title,
                "url": full_url,
                "source": source_name
            })

    return articles

# -------- MAIN FUNCTION -------- #
async def run_all_sites() -> List[Dict[str, str]]:
    sources = [
        {"name": "Benzinga", "url": "https://www.benzinga.com/recent", "filter": benzinga_filter},
        {"name": "BBC News", "url": "https://www.bbc.com/news", "filter": bbc_filter},
        {"name": "CNN", "url": "https://edition.cnn.com/world", "filter": cnn_filter},
    ]

    tasks = [
        extract_titles_and_urls(src["name"], src["url"], src["filter"])
        for src in sources
    ]
    all_results = await asyncio.gather(*tasks)
    flat_results = [item for sublist in all_results for item in sublist]

    # Deduplicate
    seen = set()
    unique = []
    for item in flat_results:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique

# -------- AGENTS -------- #
ContentExtractor = Agent(
    name="ContentExtractor",
    tools=[FirecrawlTools(), Crawl4aiTools()],
    model=groq_model,
    response_model=RawArticleData,
    parser_model=parser_model,
    description="Scrapes and extracts the raw text content from a single article URL.",
    instructions=[
        "You will be given a single URL.",
        "You MUST use the available scraping tools to fetch the page's content.",
        "Extract the page title and the main body of text. Do not summarize or alter the text.",
        "If one tool fails, try the other. Return the raw data."
    ],
    show_tool_calls=True,
    debug_mode=True,
)

ArticleFormatter = Agent(
    name="ArticleFormatter",
    model=groq_model,
    response_model=FormattedArticle,
    parser_model=parser_model,
    description="Takes raw article data and formats it into a clean, structured `FormattedArticle`.",
    instructions=[
        "You are an expert news editor.",
        "You will receive raw data containing a title, content, and a URL. Your response MUST be based ONLY on this provided data.",
        "Your sole task is to analyze the raw content and produce a clean, final article object.",
        "1.  Create a clean, engaging `title` from the raw title.",
        "2.  From the URL or content, identify the `source` (e.g., Boston.com, BBC).",
        "3.  If a publication date is present in the content, extract it and format it as YYYY-MM-DD for the `date` field. If not found, leave it as null.",
        "4.  Write a comprehensive `full_description` by summarizing the key points from the raw content. This summary must be at least 200 words.",
        "5.  Ensure the original `url` is included in the final object.",
        "CRITICAL: Do not write any explanation or introductory text. Your response must be ONLY the final JSON object that conforms to the `FormattedArticle` schema."
    ],
    debug_mode=True,
)

# -------- RUNNER -------- #
if __name__ == "__main__":
    print(f"🔎 Filtering for date in URL: {DATE_PATTERN}\n")
    raw_articles = asyncio.run(run_all_sites())

    # ✅ Print as list
    print("List Output:\n")
    for i, article in enumerate(raw_articles, 1):
        print(f"{i}. {article['title']}\n   {article['url']}")

    # ✅ JSON output
    json_output = json.dumps(raw_articles, indent=2, ensure_ascii=False)
    print("\n\nFormatted JSON Output:\n")
    print(json_output)

    # ✅ Save to JSON file
    with open("filtered_news_articles.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\n✅ Saved {len(raw_articles)} articles to filtered_news_articles.json")

    # ✅ Run agents on each article
    formatted_articles = []
    for article in raw_articles:
        try:
            raw_content = ContentExtractor.run(article["url"])
            formatted = ArticleFormatter.run({
                "title": raw_content["title"],
                "content": raw_content["content"],
                "url": article["url"]
            })
            formatted_articles.append(formatted)
        except Exception as e:
            print(f"[!] Failed to process article: {article['url']}\n    Reason: {e}")

    # ✅ Save formatted articles
    with open("formatted_news_articles.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(formatted_articles, indent=2, ensure_ascii=False))
    print(f"\n✅ Saved {len(formatted_articles)} formatted articles to formatted_news_articles.json")