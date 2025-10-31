# utils.py

import random
import re
from typing import Dict

# We need to import our config file to get user agents and headers
from Scraping_Crawling import config

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def GetHeaders() -> Dict[str, str]:
    """Generate headers with a random user agent."""
    headers = config.DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(config.USER_AGENTS)
    headers["Referer"] = "https://www.google.com/"
    return headers


def PreprocessAndClean(text: str) -> str:
    """Clean extracted text by removing newlines, tabs, and extra whitespace."""
    if not text or text.lower() in ["content not found", "not found"]:
        return text

    text = text.replace('\n', ' ').replace('\t', ' ')
    text = text.replace('\\', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def IsValidArticle(data: dict) -> bool:
    """Check if article data indicates a scraping failure."""
    invalid_strings = {"not found", "content not found"}
    for value in data.values():
        if isinstance(value, str) and value.lower() in invalid_strings:
            return False
    return True


def HasGoodTitle(title: str) -> bool:
    """Check if title looks like a real article title."""
    if not title or len(title.strip()) < 15:
        return False

    title_lower = title.lower().strip()
    skip_titles = [
        "read more", "view more", "see more", "click here", "continue reading",
        "home", "news", "latest", "breaking", "live", "watch", "listen",
        "subscribe", "newsletter", "sign up", "login", "menu", "search",
        "share", "comment", "follow", "like", "tweet", "facebook"
    ]

    if any(skip in title_lower for skip in skip_titles):
        return False

    return len(title.split()) >= 4 and any(char.isalpha() for char in title)

def IsValidArticleUrl(href: str, base_domain: str) -> bool:
    """Generic validation for article URLs."""
    if not href:
        return False
        
    skip_patterns = [
        "/video/", "/videos/", "/gallery/", "/photos/", "/images/",
        "/live/", "/livestream/", "/podcast/", "/audio/",
        "/newsletter/", "/subscription/", "/subscribe/", "/premium/",
        "/login", "/signup", "/register", "/account", "/profile",
        "/search", "/sitemap", "/contact", "/about", "/privacy",
        "/terms", "/cookies", "/rss", "/feed", "/api/",
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3",
        "#", "javascript:", "mailto:", "tel:"
    ]
    
    href_lower = href.lower()
    if any(pattern in href_lower for pattern in skip_patterns):
        return False
        
    if href.startswith('http') and base_domain not in href:
        return False
        
    return True