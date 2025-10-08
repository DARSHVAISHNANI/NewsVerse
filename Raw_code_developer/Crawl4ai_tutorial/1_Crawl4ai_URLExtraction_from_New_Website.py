import asyncio
from typing import List, Callable, Dict
from crawl4ai import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime, timedelta
import re

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

# -------- RUNNER -------- #
if __name__ == "__main__":
    print(f"🔎 Filtering for date in URL: {DATE_PATTERN}\n")
    results = asyncio.run(run_all_sites())

    # ✅ Print as list
    print("List Output:\n")
    for i, article in enumerate(results, 1):
        print(f"{i}. {article['title']}\n   {article['url']}")

    # ✅ JSON output
    json_output = json.dumps(results, indent=2, ensure_ascii=False)
    print("\n\nFormatted JSON Output:\n")
    print(json_output)

    # ✅ Save to JSON file
    with open("BBC_filtered_news_articles.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\n✅ Saved {len(results)} articles to filtered_news_articles.json")