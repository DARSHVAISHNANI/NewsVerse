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
from agno.models.openrouter import OpenRouter
from agno.models.groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

# Use a more powerful model specifically for parsing the final JSON output
parser_model = OpenRouter(id="mistralai/mistral-7b-instruct:free", api_key="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", base_url="https://openrouter.ai/api/v1")
groq_model = OpenRouter(id="mistralai/mistral-7b-instruct:free", api_key="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", base_url="https://openrouter.ai/api/v1")

# parser_model = Groq(id="meta-llama/llama-4-scout-17b-16e-instruct")
# groq_model = Groq(id="meta-llama/llama-4-scout-17b-16e-instruct")

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
        # {"name": "Benzinga", "url": "https://www.benzinga.com/recent", "filter": benzinga_filter},
        {"name": "BBC News", "url": "https://www.bbc.com/news", "filter": bbc_filter}
        # {"name": "CNN", "url": "https://edition.cnn.com/world", "filter": cnn_filter},
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
    tools=[Crawl4aiTools()],
    model=groq_model,
    response_model=None, # <-- Disable automatic parsing
    parser_model=None,   # <-- Disable the parser model
    description="Scrapes and extracts the raw text content from a single article URL.",
    instructions=[
        "You will be given a single URL.",
        "You MUST use the available scraping tools to fetch the page's content.",
        "Extract the page title and the main body of text. Do not summarize or alter the text.",
        "CRITICAL: Your response MUST be ONLY a single, valid JSON object with the keys 'title', 'content', and 'url'. Do not include any other text, explanations, or markdown formatting like ```json."
    ],
    show_tool_calls=True,
    debug_mode=True,
)

ArticleFormatter = Agent(
    name="ArticleFormatter",
    model=groq_model,
    response_model=None, # <-- Disable automatic parsing
    parser_model=None,   # <-- Disable the parser model
    description="Takes raw article data and formats it into a clean, structured `FormattedArticle`.",
    instructions=[
        "You are an expert news editor.",
        "You will receive raw data containing a title, content, source, and a URL. Your response MUST be based ONLY on this provided data.",
        "Your sole task is to analyze the raw content and produce a clean, final article object.",
        "1.  Create a clean, engaging `title` from the raw title.",
        "2.  The `source` is provided, use it directly.",
        "3.  If a publication date is present in the content, extract it and format it as YYYY-MM-DD for the `date` field. If not found, leave it as null.",
        "4.  Write a comprehensive `full_description` by summarizing the key points from the raw content. This summary must be at least 200 words.",
        "5.  Ensure the original `url` is included in the final object.",
        "CRITICAL: Do not write any explanation or introductory text. Your response must be ONLY the final JSON object that conforms to the `FormattedArticle` schema. Do not wrap it in markdown."
    ],
    debug_mode=True,
)

# -------- ASYNC RUNNER -------- #
import json
import re # <-- Add this import for cleaning the text

# -------- ASYNC RUNNER -------- #
async def main():
    """Main async function to orchestrate the entire workflow."""
    print(f"🔎 Filtering for date in URL: {DATE_PATTERN}\n")
    raw_articles = await run_all_sites()

    # Print and save the initial list of URLs
    print("List Output:\n")
    for i, article in enumerate(raw_articles, 1):
        print(f"{i}. {article['title']}\n   {article['url']}")

    with open("filtered_news_articles.json", "w", encoding="utf-8") as f:
        json.dump(raw_articles, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved {len(raw_articles)} raw article links to filtered_news_articles.json")

    # --- CONTROL CONCURRENCY ---
    # Set a limit on how many tasks can run at the same time to avoid rate limits.
    CONCURRENCY_LIMIT = 3
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def process_article(article_data: dict):
        """Asynchronously scrapes and formats a single article, respecting the semaphore."""
        async with semaphore: # This line makes the task wait its turn
            try:
                # --- EXTRACTOR STEP ---
                extractor_run = await ContentExtractor.arun(article_data["url"])
                if not hasattr(extractor_run, 'content') or not extractor_run.content:
                    print(f"⚠️  Extractor agent returned no raw text for: {article_data['url']}")
                    return None
                
                raw_text_output = extractor_run.content
                match = re.search(r'\{.*\}', raw_text_output, re.DOTALL)
                if not match:
                    print(f"⚠️  Could not find JSON in Extractor response for: {article_data['url']}")
                    return None
                
                try:
                    content_dict = json.loads(match.group(0))
                    raw_content_model = RawArticleData(**content_dict)
                except (json.JSONDecodeError, TypeError):
                    print(f"⚠️  Failed to decode JSON from Extractor for: {article_data['url']}")
                    return None

                if not raw_content_model.content or "page has been blocked" in raw_content_model.content:
                    print(f"ℹ️  Extracted content was empty or blocked for: {article_data['url']}")
                    return None

                # --- FORMATTER STEP ---
                formatter_input = {
                    "title": raw_content_model.title,
                    "content": raw_content_model.content,
                    "url": raw_content_model.url,
                    "source": article_data["source"]
                }
                formatter_run = await ArticleFormatter.arun(formatter_input)

                if not hasattr(formatter_run, 'content') or not formatter_run.content:
                    print(f"⚠️  Formatter agent returned no raw text for: {article_data['url']}")
                    return None

                formatter_raw_text = formatter_run.content
                match = re.search(r'\{.*\}', formatter_raw_text, re.DOTALL)
                if not match:
                    print(f"⚠️  Could not find JSON in Formatter response for: {article_data['url']}")
                    return None

                try:
                    formatted_dict = json.loads(match.group(0))
                    final_article = FormattedArticle(**formatted_dict)
                    print(f"✅ Successfully processed: {final_article.title}")
                    return final_article
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"⚠️  Failed to decode JSON from Formatter for: {article_data['url']}. Error: {e}")
                    return None

            except Exception as e:
                print(f"❗️ Critical failure while processing article: {article_data['url']}\n    Reason: {e}")
                return None

    print(f"\n🚀 Processing articles with AI agents (Concurrency limit: {CONCURRENCY_LIMIT})...")
    tasks = [process_article(article) for article in raw_articles]
    results = await asyncio.gather(*tasks)

    formatted_articles = [res for res in results if res is not None]

    if formatted_articles:
        with open("formatted_news_articles.json", "w", encoding="utf-8") as f:
            json_data = [article.model_dump() for article in formatted_articles]
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(formatted_articles)} formatted articles to formatted_news_articles.json")
    else:
        print("\n⚠️ No articles were successfully formatted.")


if __name__ == "__main__":
    asyncio.run(main())