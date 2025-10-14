import asyncio
import json
import os
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlResult

# Import from our new modules
from config import *
from parsers import PARSERS
from utils import GetHeaders, PreprocessAndClean, HasGoodTitle, IsValidArticleUrl


def BBCFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for BBC news articles."""
    return (HasGoodTitle(title) and 
            IsValidArticleUrl(href, "bbc.com") and 
            ("/news/articles/" in href or 
             (href.count('-') > 2 and href.rstrip('/')[-1].isdigit())))


def CNNFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for CNN news articles."""
    if not HasGoodTitle(title) or not IsValidArticleUrl(href, "cnn.com"):
        return False
        
    if not href.endswith(".html"):
        return False
    
    categories = [
        "/world/", "/politics/", "/business/", "/health/",
        "/entertainment/", "/travel/", "/style/", "/sport/", "/us/", "/middleeast/"
    ]
    
    contains_year = any(year in href for year in ["/2025/"])
    contains_category = any(cat in href for cat in categories)
    
    return contains_year or contains_category


def IndianExpressFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for Indian Express articles."""
    return (HasGoodTitle(title) and 
            IsValidArticleUrl(href, "indianexpress.com") and 
            ("/article/" in href or href.count('-') > 3))


def IndiaTodayFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for India Today articles."""
    return (HasGoodTitle(title) and
            IsValidArticleUrl(href, "indiatoday.in") and
            "/story/" in href and
            href.count('-') > 3)


def HTFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for Hindustan Times articles."""
    return (HasGoodTitle(title) and
            IsValidArticleUrl(href, "hindustantimes.com") and
            ".html" in href and
            href.count('-') > 3 and
            href.rstrip('.html')[-1].isdigit())


def TOIFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for Times of India articles."""
    return (HasGoodTitle(title) and
            IsValidArticleUrl(href, "indiatimes.com") and
            "/articleshow/" in href and
            href.endswith(".cms"))


def ReutersFilter(href: str, title: str, base_url: str) -> bool:
    """Filter for Reuters articles."""
    return (HasGoodTitle(title) and 
            IsValidArticleUrl(href, "reuters.com") and 
            any(p in href for p in [
                "/world/", "/business/", "/technology/", "/markets/", "/legal/",
                "/sustainability/", "/breakingviews/", "/lifestyle/"
            ]) and ("/article/" in href or any(x in href for x in ["2024", "2025"])))


# News sources configuration
NEWS_SOURCES = [
    {
        "name": "BBC",
        "url": "https://www.bbc.com/news",
        "filter": BBCFilter,
        "backup_urls": ["https://www.bbc.com/news/world", "https://www.bbc.com/news/technology"]
    },
    {
        "name": "IndianExpress",
        "url": "https://indianexpress.com/",
        "filter": IndianExpressFilter,
        "backup_urls": ["https://indianexpress.com/section/india/", "https://indianexpress.com/section/world/"]
    },
    {
        "name": "IndiaToday",
        "url": "https://www.indiatoday.in/",
        "filter": IndiaTodayFilter,
        "backup_urls": ["https://www.indiatoday.in/india", "https://www.indiatoday.in/world"]
    },
    {
        "name": "HT",
        "url": "https://www.hindustantimes.com/",
        "filter": HTFilter,
        "backup_urls": ["https://www.hindustantimes.com/india-news", "https://www.hindustantimes.com/world-news"]
    },
    {
        "name": "TOI",
        "url": "https://timesofindia.indiatimes.com/",
        "filter": TOIFilter,
        "backup_urls": ["https://timesofindia.indiatimes.com/india", "https://timesofindia.indiatimes.com/world"]
    },
    {
        "name": "Reuters",
        "url": "https://www.reuters.com/world/",
        "filter": ReutersFilter,
        "backup_urls": ["https://www.reuters.com/business/", "https://www.reuters.com/technology/"]
    }
]

# =============================================================================
# CRAWLER SETUP
# =============================================================================

async def CreateCrawler() -> AsyncWebCrawler:
    """Create optimized crawler with anti-detection measures."""
    crawler = AsyncWebCrawler()
    crawler.playwright_context_args = {
        "wait_until": "domcontentloaded",
        "timeout": 60000,
        "extra_http_headers": GetHeaders(),
        "java_script_enabled": True,
        "viewport": {"width": 1920, "height": 1080},
        "extra_scripts": [
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.navigator.chrome = { runtime: {} };
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
        ]
    }
    return crawler


async def ExtractArticlesFromSource(source_config: Dict, crawler: AsyncWebCrawler) -> List[Dict]:
    """
    Extract article URLs from a single news source.
    
    Args:
        source_config: Configuration for the news source
        crawler: Configured web crawler
        
    Returns:
        List of discovered article dictionaries
    """
    source_name = source_config["name"]
    all_urls_to_try = [source_config["url"]] + source_config.get("backup_urls", [])
    articles = []
    processed_urls = set()

    print(f"🔍 Starting discovery for {source_name}...")
    
    for url_to_crawl in all_urls_to_try:
        if len(articles) >= MAX_ARTICLES_PER_SOURCE:
            break
            
        try:
            result: CrawlResult = await crawler.arun(url_to_crawl)
            if not result.success or not result.cleaned_html:
                print(f"   - Failed to crawl {url_to_crawl}")
                continue
            
            print(f"   - Processing {url_to_crawl}")
            soup = BeautifulSoup(result.cleaned_html, "html.parser")
            links = soup.find_all("a", href=True)
            
            for link in links:
                if len(articles) >= MAX_ARTICLES_PER_SOURCE:
                    break
                
                href = link.get("href", "")
                title = link.get_text(strip=True)
                
                if not href or not title:
                    continue
                
                full_url = urljoin(url_to_crawl, href)
                
                if full_url in processed_urls:
                    continue

                if source_config["filter"](href, title, url_to_crawl):
                    articles.append({
                        "source": source_name,
                        "url": full_url
                    })
                    processed_urls.add(full_url)
                    
        except Exception as e:
            print(f"   - An error occurred while crawling {url_to_crawl}: {e}")
            continue
            
    print(f"   => Discovered {len(articles)} articles for {source_name}.")
    return articles


async def DiscoverAllArticles() -> List[Dict]:
    """
    Discover articles from all configured news sources.
    
    Returns:
        List of all discovered article dictionaries
    """
    crawler = await CreateCrawler()
    all_articles = []
    
    async with crawler as crawler:
        for source_config in NEWS_SOURCES:
            try:
                articles = await ExtractArticlesFromSource(source_config, crawler)
                all_articles.extend(articles)
                await asyncio.sleep(random.uniform(1, 3))  # Be respectful
            except Exception as e:
                print(f"Failed to process source {source_config['name']}: {e}")
                continue
    
    return all_articles


# =============================================================================
# CONTENT PROCESSING FUNCTIONS
# =============================================================================

def ProcessArticle(item: Dict, session: requests.Session) -> Optional[Dict]:
    """
    Process a single article: extract, clean, and return all data.
    
    Args:
        item: Article item with source and URL
        session: HTTP session for requests
        
    Returns:
        Processed article data or None if failed
    """
    source = item['source']
    url = item['url']
    parser = PARSERS.get(source)
    
    if not parser:
        return None

    try:
        response = session.get(url, headers=GetHeaders(), timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract raw data
        raw_title = parser["title"](soup)
        pub_date, pub_time = parser["date"](soup)
        raw_content = parser["content"](soup)

        # Clean the extracted data
        cleaned_title = PreprocessAndClean(raw_title)
        cleaned_content = PreprocessAndClean(raw_content)

        return {
            "source": source,
            "title": cleaned_title,
            "date": pub_date,
            "time": pub_time,
            "content": cleaned_content,
            "url": url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"   - Request failed for {url}: {e}")
        return None