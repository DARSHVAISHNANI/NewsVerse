import asyncio
import json
import re
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler, CrawlResult
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# We will still use dateutil.parser for its power
from dateutil.parser import parse as date_parse

# --------- CONFIG --------- #
INPUT_FILENAME = "BBC_filtered_news_articles.json"
OUTPUT_FILENAME = "BBC_scraped_article_details.json"

# --- HELPER FUNCTIONS --- #

def load_articles_from_json(filename: str) -> List[Dict]:
    """Loads the list of articles from the initial JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Input file '{filename}' not found.")
        print("Please run the first script to generate it.")
        return []
    except json.JSONDecodeError:
        print(f"[!] Error: Could not read '{filename}'. Make sure it's a valid JSON file.")
        return []

# --- FINAL PARSING LOGIC --- #

def parse_article_details(soup: BeautifulSoup) -> Dict:
    """
    Final version: Handles absolute dates, relative dates, and finds content more reliably.
    """
    found_date = "Not Found"
    found_time = "Not Found"
    
    # --- Step 1: Try to find an ABSOLUTE date first ---
    # Methods A, B, C: Check structured data, meta tags, and time tags.
    potential_datestrings = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if 'datePublished' in data: potential_datestrings.append(data['datePublished'])
            if 'dateModified' in data: potential_datestrings.append(data['dateModified'])
        except (json.JSONDecodeError, TypeError): continue
    
    time_tag = soup.find('time', attrs={'datetime': True})
    if time_tag: potential_datestrings.append(time_tag['datetime'])
    
    for meta in soup.find_all('meta', attrs={'property': ['article:published_time', 'og:published_time']}):
        potential_datestrings.append(meta['content'])

    for datestring in potential_datestrings:
        try:
            dt_obj = date_parse(datestring)
            found_date = dt_obj.strftime('%Y-%m-%d')
            found_time = dt_obj.strftime('%H:%M:%S')
            break # Stop once we find one
        except (ValueError, TypeError): continue
    
    # --- Step 2: If no absolute date, look for RELATIVE dates (e.g., "4 hours ago") ---
    if found_date == "Not Found":
        # Regex to find patterns like "X hours ago", "Y minutes ago", etc.
        relative_date_pattern = re.compile(r'(\d+)\s+(hour|minute|day)s?\s+ago', re.IGNORECASE)
        match = relative_date_pattern.search(soup.get_text())
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()
            
            delta_args = {f"{unit}s": value} # e.g., hours=4
            past_datetime = datetime.now() - timedelta(**delta_args)
            
            found_date = past_datetime.strftime('%Y-%m-%d')
            found_time = past_datetime.strftime('%H:%M:%S')

    # --- Step 3: Find content using a priority list of selectors ---
    content = "Content not found"
    # This list tries common selectors for articles from most specific to most general
    content_selectors = [
        'article',
        'div[class*="article-body"]',
        'div[class*="post-body"]',
        'div[class*="post-content"]',
        'div[class*="entry-content"]',
        'main#main-content' # A common tag for the main section
    ]
    for selector in content_selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get_text(separator='\n', strip=True)
            break # Stop once we find content

    return {"date": found_date, "time": found_time, "content": content}


async def scrape_single_article(article_info: Dict, crawler: AsyncWebCrawler) -> Optional[Dict]:
    """Scrapes one URL and extracts the required details."""
    url = article_info.get("url")
    if not url: return None

    print(f"-> Scraping {url}")
    result: CrawlResult = await crawler.arun(url)

    if not result.success or not result.cleaned_html:
        print(f"[!] Failed to crawl {url}")
        return {**article_info, "date": "Crawl Failed", "time": "Crawl Failed", "content": "Crawl Failed"}

    soup = BeautifulSoup(result.cleaned_html, "html.parser")
    extracted_data = parse_article_details(soup)
    return {**article_info, **extracted_data}


# --- MAIN ORCHESTRATOR --- #
async def main():
    """Main function to orchestrate the scraping process."""
    articles_to_scrape = load_articles_from_json(INPUT_FILENAME)
    if not articles_to_scrape: return

    print(f"✅ Found {len(articles_to_scrape)} articles to scrape from '{INPUT_FILENAME}'.\n")

    async with AsyncWebCrawler() as crawler:
        tasks = [scrape_single_article(article, crawler) for article in articles_to_scrape]
        all_results = await asyncio.gather(*tasks)

    successful_results = [res for res in all_results if res is not None]

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(successful_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Saved details for {len(successful_results)} articles to '{OUTPUT_FILENAME}'.")


# --- RUNNER --- #
if __name__ == "__main__":
    asyncio.run(main())