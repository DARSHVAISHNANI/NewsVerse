import json
import re
from datetime import datetime
from typing import Tuple

import pytz
from bs4 import BeautifulSoup
from dateutil import parser


# BBC Parsers
def ExtractTitleBBC(soup: BeautifulSoup) -> str:
    """Extract title from BBC article."""
    selectors = [
        "h1[id^='main-heading']",
        "h1.ssrcss-1pl2zfy-Heading",
        "meta[property='og:title']",
        "meta[name='twitter:title']",
        "title"
    ]
    
    for selector in selectors:
        if selector.startswith("meta"):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                return tag.get("content").strip()
        elif selector == "title":
            if soup.title and soup.title.string:
                return soup.title.string.strip()
        else:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
    
    return "Title not found"


def ExtractDateBBC(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from BBC article."""
    selectors = [
        "time[datetime]",
        "span[data-testid='timestamp']",
        "meta[property='article:published_time']"
    ]
    
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            date_str = tag.get("datetime") or tag.get("content") or tag.get_text(strip=True)
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
            except:
                pass
    
    return "Not Found", "Not Found"


def ExtractContentBBC(soup: BeautifulSoup) -> str:
    """Extract content from BBC article."""
    selectors = [
        "div[data-component='text-block'] p",
        "div.ssrcss-7uxr49-RichTextContainer p",
        "main article p:not([class*='caption'])"
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if len(elements) >= 2:
            return " ".join(e.get_text(strip=True) for e in elements)
    
    return "Content not found"


# Indian Express Parsers
def ExtractTitleIndianExpress(soup: BeautifulSoup) -> str:
    """Extract title from Indian Express article."""
    selectors = [
        "h1.native_story_title",
        "meta[property='og:title']",
        "title"
    ]
    
    for selector in selectors:
        if selector.startswith("meta"):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                return tag.get("content").strip()
        elif selector == "title":
            if soup.title and soup.title.string:
                return soup.title.string.strip()
        else:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
    
    return "Title not found"


def ExtractDateIndianExpress(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from Indian Express article."""
    selectors = [
        "span[itemprop='dateModified']",
        "meta[property='article:published_time']"
    ]
    
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            date_str = tag.get("content") or tag.get_text(strip=True)
            if not date_str:
                continue
            
            try:
                dt_obj = parser.parse(date_str)
                if dt_obj.tzinfo is None:
                    ist_tz = pytz.timezone("Asia/Kolkata")
                    dt_obj = ist_tz.localize(dt_obj)
                
                return dt_obj.strftime("%Y-%m-%d"), dt_obj.strftime("%H:%M:%S")
            except (ValueError, parser.ParserError):
                continue
    
    return "Not Found", "Not Found"


def ExtractContentIndianExpress(soup: BeautifulSoup) -> str:
    """Extract content from Indian Express article."""
    content_container = soup.select_one("#pcl-full-content")
    if content_container:
        paragraphs = content_container.select("p:not(.ad-pro-label)")
        if len(paragraphs) >= 2:
            return " ".join(p.get_text(strip=True) for p in paragraphs)
    
    story_details = soup.select("div.story_details p")
    if len(story_details) >= 2:
        return " ".join(p.get_text(strip=True) for p in story_details)
    
    return "Content not found"


# India Today Parsers
def ExtractTitleIndiaToday(soup: BeautifulSoup) -> str:
    """Extract title from India Today article."""
    selectors = [
        "h1.story-kicker-title",
        "meta[property='og:title']",
        "title"
    ]
    
    for selector in selectors:
        if selector.startswith("meta"):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                return tag.get("content").strip()
        elif selector == "title":
            if soup.title and soup.title.string:
                return soup.title.string.strip()
        else:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
    
    return "Title not found"


def ExtractDateIndiaToday(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from India Today article."""
    selectors = [
        "div.story-kicker-updated-date",
        "meta[property='article:published_time']"
    ]
    
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            date_str = tag.get("content") or tag.get_text(strip=True)
            if not date_str:
                continue
            
            try:
                dt_aware = parser.parse(date_str, fuzzy=True)
                if dt_aware.tzinfo is None:
                    ist_tz = pytz.timezone("Asia/Kolkata")
                    dt_aware = ist_tz.localize(dt_aware)
                else:
                    dt_aware = dt_aware.astimezone(pytz.timezone("Asia/Kolkata"))
                
                return dt_aware.strftime("%Y-%m-%d"), dt_aware.strftime("%H:%M:%S")
            except (ValueError, parser.ParserError):
                continue
    
    return "Not Found", "Not Found"


def ExtractContentIndiaToday(soup: BeautifulSoup) -> str:
    """Extract content from India Today article."""
    selectors = [
        "div.story-content p",
        "div.story-kicker-content p",
        "div.description p"
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if len(elements) >= 2:
            return " ".join(p.get_text(strip=True) for p in elements)
    
    return "Content not found"


# Hindustan Times Parsers
def ExtractTitleHT(soup: BeautifulSoup) -> str:
    """Extract title from Hindustan Times article."""
    selectors = [
        "h1.hdg1",
        "meta[property='og:title']",
        "title"
    ]
    
    for selector in selectors:
        if selector.startswith("meta"):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                return tag.get("content").strip()
        elif selector == "title":
            if soup.title and soup.title.string:
                return soup.title.string.strip()
        else:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
    
    return "Title not found"


def ExtractDateHT(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from Hindustan Times article."""
    # Try JSON-LD script first
    try:
        for script in soup.find_all("script", type="application/ld+json"):
            script_content = script.string.strip()
            data = json.loads(script_content)
            
            if isinstance(data, list):
                data = data[0]
            
            date_str = data.get("datePublished") or data.get("dateModified")
            if date_str:
                dt_aware = parser.parse(date_str)
                ist_tz = pytz.timezone("Asia/Kolkata")
                dt_ist = dt_aware.astimezone(ist_tz)
                return dt_ist.strftime("%Y-%m-%d"), dt_ist.strftime("%H:%M:%S")
    except Exception:
        pass

    # Fallback to visible date elements
    try:
        date_selectors = ["div.dateTime span", "span.timeStamp"]
        for selector in date_selectors:
            tag = soup.select_one(selector)
            if tag and tag.text:
                dt_aware = parser.parse(tag.text, fuzzy=True)
                ist_tz = pytz.timezone("Asia/Kolkata")
                dt_ist = dt_aware.astimezone(ist_tz)
                return dt_ist.strftime("%Y-%m-%d"), dt_ist.strftime("%H:%M:%S")
    except Exception:
        pass
    
    return "Not Found", "Not Found"


def ExtractContentHT(soup: BeautifulSoup) -> str:
    """Extract content from Hindustan Times article."""
    content_selectors = [
        "div.storyDetails p",
        "div.liveBlogBody p",
    ]

    for selector in content_selectors:
        elements = soup.select(selector)
        if len(elements) >= 2:
            return " ".join(p.get_text(strip=True) for p in elements)
    
    return "Content not found"


# Times of India Parsers
def ExtractTitleTOI(soup: BeautifulSoup) -> str:
    """Extract title from Times of India article."""
    selectors = [
        "meta[property='og:title']",
        "h1._2NFXP",
        "title"
    ]
    
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            title_text = tag.get("content") or tag.get_text()
            if title_text:
                return title_text.split(' - Times of India')[0].split(' | India News')[0].strip()
    
    return "Title not found"


def ExtractDateTOI(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from Times of India article."""
    try:
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]

                date_str = data.get("dateModified") or data.get("datePublished")
                if date_str:
                    dt_aware = parser.parse(date_str)
                    ist_tz = pytz.timezone("Asia/Kolkata")
                    dt_ist = dt_aware.astimezone(ist_tz)
                    return dt_ist.strftime("%Y-%m-%d"), dt_ist.strftime("%H:%M:%S")
    except Exception:
        pass
    
    return "Not Found", "Not Found"


def ExtractContentTOI(soup: BeautifulSoup) -> str:
    """Extract content from Times of India article."""
    content_container = soup.find("div", {"data-articlebody": "true"})
    
    if not content_container:
        content_container = soup.select_one("div._s30J")

    if content_container:
        content = content_container.get_text(separator=" ", strip=True)
        if content:
            return content
    
    return "Content not found"


# Reuters Parsers
def ExtractTitleReuters(soup: BeautifulSoup) -> str:
    """Extract title from Reuters article."""
    tag = soup.find("h1", {"data-testid": "Heading"})
    if tag:
        return tag.get_text(strip=True)
    
    meta_tag = soup.select_one("meta[property='og:title']")
    if meta_tag and meta_tag.get("content"):
        return meta_tag.get("content").strip()
    
    return "Title not found"


def ExtractDateReuters(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract date from Reuters article."""
    try:
        ld_json_script = soup.find("script", type="application/ld+json")
        if ld_json_script and ld_json_script.string:
            data = json.loads(ld_json_script.string)
            if isinstance(data, list):
                data = data[0]
            
            date_str = data.get("dateModified") or data.get("datePublished")
            if date_str:
                dt_aware = parser.parse(date_str)
                ist_tz = pytz.timezone("Asia/Kolkata")
                dt_ist = dt_aware.astimezone(ist_tz)
                return dt_ist.strftime("%Y-%m-%d"), dt_ist.strftime("%H:%M:%S")
    except Exception:
        pass
    
    return "Not Found", "Not Found"


def ExtractContentReuters(soup: BeautifulSoup) -> str:
    """Extract content from Reuters article."""
    content_container = soup.find("div", {"data-testid": "ArticleBody"})
    if not content_container:
        return "Content not found"

    # Remove image captions
    for caption in content_container.find_all("figcaption"):
        caption.decompose()

    # Collect all paragraphs
    paragraphs = []
    for para in content_container.find_all("div", {"data-testid": re.compile("^paragraph-")}):
        text = para.get_text(" ", strip=True)
        if text:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)

    # Remove external link markers
    full_text = full_text.replace(", opens new tab", "")

    # Remove Reuters dateline
    dateline_marker = "(Reuters) -"
    marker_pos = full_text.find(dateline_marker)
    if marker_pos != -1:
        full_text = full_text[marker_pos + len(dateline_marker):].strip()

    # Truncate boilerplate
    stop_phrases = ["Reporting by", "Editing by", "Our Standards:", "Sign up here"]
    stop_index = -1
    for phrase in stop_phrases:
        found_index = full_text.find(phrase)
        if found_index != -1:
            if stop_index == -1 or found_index < stop_index:
                stop_index = found_index
    
    if stop_index != -1:
        full_text = full_text[:stop_index]

    if len(full_text.split()) > 15:
        return full_text.strip()
    else:
        return "Content not found"


# Parser configuration
PARSERS = {
    "BBC": {
        "title": ExtractTitleBBC,
        "date": ExtractDateBBC,
        "content": ExtractContentBBC
    },
    "IndianExpress": {
        "title": ExtractTitleIndianExpress,
        "date": ExtractDateIndianExpress,
        "content": ExtractContentIndianExpress
    },
    "IndiaToday": {
        "title": ExtractTitleIndiaToday,
        "date": ExtractDateIndiaToday,
        "content": ExtractContentIndiaToday
    },
    "HT": {
        "title": ExtractTitleHT,
        "date": ExtractDateHT,
        "content": ExtractContentHT
    },
    "TOI": {
        "title": ExtractTitleTOI,
        "date": ExtractDateTOI,
        "content": ExtractContentTOI
    },
    "Reuters": {
        "title": ExtractTitleReuters,
        "date": ExtractDateReuters,
        "content": ExtractContentReuters
    }
}