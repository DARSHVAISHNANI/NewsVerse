import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Response Models (keeping your existing models)
class ArticleURL(BaseModel):
    """Model for individual article URL with metadata"""
    url: str = Field(..., description="The full URL of the article")
    title: str = Field(default="", description="Article title if available")
    published_date: Optional[str] = Field(default=None, description="Publication date if available")
    source: str = Field(..., description="Source website name")

class ExtractedURLs(BaseModel):
    """Model for collection of extracted article URLs"""
    urls: List[ArticleURL] = Field(..., description="List of extracted article URLs")
    source_website: str = Field(..., description="The source website name")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class RawArticleData(BaseModel):
    """Model for scraped article content"""
    url: str = Field(..., description="The article URL")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Full article content")
    author: Optional[str] = Field(default=None, description="Article author")
    published_date: Optional[str] = Field(default=None, description="Publication date")
    source: str = Field(..., description="Source website")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class FormattedArticle(BaseModel):
    """Model for AI-formatted article content"""
    url: str = Field(..., description="The article URL")
    title: str = Field(..., description="Clean, formatted article title")
    summary: str = Field(..., description="AI-generated article summary")
    content: str = Field(..., description="Clean, formatted article content")
    key_points: List[str] = Field(..., description="Key points extracted from the article")
    author: Optional[str] = Field(default=None, description="Article author")
    published_date: Optional[str] = Field(default=None, description="Publication date")
    source: str = Field(..., description="Source website")
    category: Optional[str] = Field(default=None, description="AI-determined article category")
    sentiment: Optional[str] = Field(default=None, description="Article sentiment (positive/negative/neutral)")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ProcessedNewsData(BaseModel):
    """Model for final processed news data"""
    articles: List[FormattedArticle] = Field(..., description="List of processed articles")
    total_articles: int = Field(..., description="Total number of articles processed")
    sources: List[str] = Field(..., description="List of source websites")
    processing_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# News Website Configurations
NEWS_WEBSITES = {
    "bbc": {
        "url": "https://www.bbc.com/news",
        "name": "BBC News",
        "article_selectors": [
            'a[href*="/news/"]',
            'a[data-testid="internal-link"]',
            '.gel-layout__item a[href*="/news/"]'
        ]
    },
    "cnn": {
        "url": "https://www.cnn.com",
        "name": "CNN",
        "article_selectors": [
            'a[href*="/2024/"]',
            'a[href*="/2025/"]',
            '.container__link',
            'a[data-link-type="article"]'
        ]
    },
    "benzinga": {
        "url": "https://www.benzinga.com/news",
        "name": "Benzinga",
        "article_selectors": [
            'a[href*="/news/"]',
            '.story-item a',
            'a[href*="/story/"]'
        ]
    },
    "times_of_india": {
        "url": "https://timesofindia.indiatimes.com",
        "name": "Times of India",
        "article_selectors": [
            'a[href*="timesofindia.indiatimes.com"]',
            '.story-list a',
            'a[href*="/articleshow/"]'
        ]
    },
    "reuters": {
        "url": "https://www.reuters.com",
        "name": "Reuters",
        "article_selectors": [
            'a[href*="/world/"]',
            'a[href*="/business/"]',
            'a[href*="/technology/"]',
            'a[data-testid="Heading"]'
        ]
    },
    "guardian": {
        "url": "https://www.theguardian.com",
        "name": "The Guardian",
        "article_selectors": [
            'a[href*="/2024/"]',
            'a[href*="/2025/"]',
            '.fc-item__link',
            'a[data-link-name="article"]'
        ]
    }
}

# Initialize models
parser_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")
groq_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")

# AI Content Processing Agent
ContentProcessorAgent = Agent(
    name="ContentProcessor",
    tools=[],
    model=groq_model,
    response_model=FormattedArticle,
    parser_model=parser_model,
    description="Processes and formats raw article content using AI",
    instructions=[
        "You will receive raw article content extracted from a webpage.",
        "Your task is to clean, format, and enhance the article data.",
        "Extract and clean the article title, removing any site branding or navigation text.",
        "Generate a concise 2-3 sentence summary of the article.",
        "Clean the main content by removing ads, navigation, and irrelevant text.",
        "Extract 3-5 key points from the article as bullet points.",
        "Determine the article category (e.g., Politics, Technology, Business, Sports, etc.).",
        "Analyze the sentiment (positive, negative, or neutral).",
        "Preserve the author and publication date if available.",
        "Ensure all text is clean, readable, and properly formatted.",
        "Return the data in the exact FormattedArticle model structure.",
        "If content is insufficient or extraction failed, indicate this in the appropriate fields.",
    ],
    show_tool_calls=True,
    debug_mode=False,
)

class HybridNewsExtractor:
    """Hybrid implementation: Direct URL extraction + AI content processing"""
    
    def __init__(self, max_articles_per_source: int = 10):
        self.max_articles_per_source = max_articles_per_source
        from crawl4ai import AsyncWebCrawler
        self.crawler = AsyncWebCrawler()
        self.content_processor = ContentProcessorAgent
    
    async def extract_urls_direct(self, source_key: str) -> ExtractedURLs:
        """Direct URL extraction using Crawl4ai (unchanged from your version)"""
        source_config = NEWS_WEBSITES[source_key]
        
        try:
            async with self.crawler as crawler:
                result = await crawler.arun(
                    url=source_config['url'],
                    css_selector=','.join(source_config['article_selectors']),
                    extraction_strategy="css",
                    bypass_cache=True
                )
                
                if result.success:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    article_urls = []
                    for selector in source_config['article_selectors']:
                        links = soup.select(selector)
                        for link in links[:self.max_articles_per_source]:
                            href = link.get('href')
                            if href:
                                # Convert relative URLs to absolute
                                if href.startswith('/'):
                                    from urllib.parse import urljoin
                                    href = urljoin(source_config['url'], href)
                                elif not href.startswith('http'):
                                    continue
                                
                                title = link.get_text(strip=True) or link.get('title', '')
                                
                                if self._is_valid_article_url(href, source_key):
                                    article_urls.append(ArticleURL(
                                        url=href,
                                        title=title,
                                        published_date=None,
                                        source=source_config['name']
                                    ))
                    
                    # Remove duplicates
                    seen_urls = set()
                    unique_articles = []
                    for article in article_urls:
                        if article.url not in seen_urls:
                            seen_urls.add(article.url)
                            unique_articles.append(article)
                    
                    return ExtractedURLs(
                        urls=unique_articles[:self.max_articles_per_source],
                        source_website=source_config['name'],
                        extraction_timestamp=datetime.now().isoformat()
                    )
                else:
                    raise Exception(f"Failed to crawl {source_config['url']}: {result.error_message}")
                    
        except Exception as e:
            print(f"Direct extraction error for {source_key}: {str(e)}")
            return ExtractedURLs(
                urls=[],
                source_website=source_config['name'],
                extraction_timestamp=datetime.now().isoformat()
            )
    
    def _is_valid_article_url(self, url: str, source_key: str) -> bool:
        """Filter out non-article URLs (unchanged from your version)"""
        url_lower = url.lower()
        
        exclude_patterns = [
            '/video/', '/live/', '/weather/', '/sports/scores',
            '/newsletters/', '/podcasts/', '/radio/',
            'facebook.com', 'twitter.com', 'instagram.com',
            'mailto:', 'javascript:', '#', '/search',
            '/subscribe', '/login', '/register'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        if source_key == 'cnn':
            return '/2024/' in url or '/2025/' in url
        elif source_key == 'bbc':
            return '/news/' in url
        elif source_key == 'benzinga':
            return '/news/' in url or '/story/' in url
        elif source_key == 'times_of_india':
            return 'articleshow' in url
        
        return True
    
    async def extract_raw_content(self, article_url: ArticleURL) -> RawArticleData:
        """Extract raw content using Crawl4ai"""
        try:
            async with self.crawler as crawler:
                result = await crawler.arun(
                    url=article_url.url,
                    extraction_strategy="basic",
                    bypass_cache=True,
                    remove_unwanted_tags=['script', 'style', 'nav', 'footer', 'aside'],
                    only_text=True
                )
                
                if result.success:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    # Try to find title
                    title = None
                    for title_selector in ['h1', '.headline', '.article-title', 'title']:
                        title_elem = soup.select_one(title_selector)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break
                    
                    content = result.extracted_content or "No content extracted"
                    
                    # Try to find author
                    author = None
                    for author_selector in ['.author', '.byline', '[rel="author"]']:
                        author_elem = soup.select_one(author_selector)
                        if author_elem:
                            author = author_elem.get_text(strip=True)
                            break
                    
                    return RawArticleData(
                        url=article_url.url,
                        title=title or article_url.title or "No title found",
                        content=content,
                        author=author,
                        published_date=None,
                        source=article_url.source,
                        extraction_timestamp=datetime.now().isoformat()
                    )
                else:
                    raise Exception(f"Failed to extract content: {result.error_message}")
                    
        except Exception as e:
            print(f"Raw content extraction error for {article_url.url}: {str(e)}")
            return RawArticleData(
                url=article_url.url,
                title=article_url.title or "Error: Could not extract title",
                content=f"Error extracting content: {str(e)}",
                source=article_url.source,
                extraction_timestamp=datetime.now().isoformat()
            )
    
    async def process_content_with_ai(self, raw_article: RawArticleData) -> FormattedArticle:
        """Process raw content using AI agent"""
        processing_prompt = f"""
TASK: Process and format the following raw article content.

ARTICLE DATA:
- URL: {raw_article.url}
- Source: {raw_article.source}
- Raw Title: {raw_article.title}
- Author: {raw_article.author or "Unknown"}
- Published Date: {raw_article.published_date or "Unknown"}

RAW CONTENT:
{raw_article.content[:3000]}...  # Truncated for processing

INSTRUCTIONS:
1. Clean and format the title (remove site branding, navigation text)
2. Generate a 2-3 sentence summary
3. Clean the content (remove ads, navigation, irrelevant text)
4. Extract 3-5 key points as a list
5. Determine the article category (Politics, Business, Technology, Sports, etc.)
6. Analyze sentiment (positive, negative, neutral)
7. Preserve author and date information

OUTPUT: Return a properly formatted FormattedArticle object with all fields filled.
        """
        
        try:
            result = await self.content_processor.arun(processing_prompt)
            
            # Handle different response types
            if hasattr(result, 'url') and hasattr(result, 'title'):
                return result
            elif isinstance(result, dict):
                return FormattedArticle(**result)
            elif isinstance(result, str):
                try:
                    data = json.loads(result)
                    return FormattedArticle(**data)
                except:
                    pass
            
            # Fallback: create basic formatted version
            return FormattedArticle(
                url=raw_article.url,
                title=raw_article.title,
                summary="Summary could not be generated by AI",
                content=raw_article.content,
                key_points=["Content processing failed"],
                author=raw_article.author,
                published_date=raw_article.published_date,
                source=raw_article.source,
                category="Unknown",
                sentiment="neutral",
                extraction_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"AI processing error for {raw_article.url}: {str(e)}")
            return FormattedArticle(
                url=raw_article.url,
                title=raw_article.title,
                summary=f"AI processing failed: {str(e)}",
                content=raw_article.content,
                key_points=[f"Error: {str(e)}"],
                author=raw_article.author,
                published_date=raw_article.published_date,
                source=raw_article.source,
                category="Error",
                sentiment="neutral",
                extraction_timestamp=datetime.now().isoformat()
            )
    
    async def run_hybrid_pipeline(self, source_keys: List[str] = None, max_articles: int = 20) -> ProcessedNewsData:
        """Run the complete hybrid pipeline"""
        if source_keys is None:
            source_keys = list(NEWS_WEBSITES.keys())
        
        print(f"Starting hybrid extraction pipeline for sources: {source_keys}")
        
        # Stage 1: Extract URLs (Direct method)
        print("Stage 1: Extracting article URLs...")
        all_article_urls = []
        for source_key in source_keys:
            print(f"  Extracting URLs from {source_key}...")
            url_result = await self.extract_urls_direct(source_key)
            all_article_urls.extend(url_result.urls)
            print(f"  Found {len(url_result.urls)} URLs from {source_key}")
        
        print(f"Total URLs extracted: {len(all_article_urls)}")
        
        # Limit articles to process
        articles_to_process = all_article_urls[:max_articles]
        print(f"Processing {len(articles_to_process)} articles...")
        
        # Stage 2: Extract raw content
        print("Stage 2: Extracting raw content...")
        raw_articles = []
        for i, article_url in enumerate(articles_to_process):
            print(f"  Extracting content {i+1}/{len(articles_to_process)}: {article_url.title[:50]}...")
            raw_content = await self.extract_raw_content(article_url)
            if len(raw_content.content) > 100 and "Error" not in raw_content.content:
                raw_articles.append(raw_content)
        
        print(f"Successfully extracted {len(raw_articles)} articles")
        
        # Stage 3: Process with AI
        print("Stage 3: Processing content with AI...")
        formatted_articles = []
        for i, raw_article in enumerate(raw_articles):
            print(f"  AI processing {i+1}/{len(raw_articles)}: {raw_article.title[:50]}...")
            formatted_article = await self.process_content_with_ai(raw_article)
            formatted_articles.append(formatted_article)
        
        # Final results
        final_results = ProcessedNewsData(
            articles=formatted_articles,
            total_articles=len(formatted_articles),
            sources=list(set([article.source for article in formatted_articles])),
            processing_timestamp=datetime.now().isoformat()
        )
        
        print(f"Pipeline complete! Processed {final_results.total_articles} articles")
        return final_results

# Updated main function
async def main():
    """Main function using the hybrid approach"""
    
    print("Starting Hybrid News Extraction Pipeline")
    print("=" * 50)
    
    # Configuration
    sources_to_scrape = ["bbc", "cnn", "benzinga"]  # Add more as needed
    max_articles_to_process = 15  # Adjust based on your needs
    
    try:
        # Initialize the hybrid extractor
        extractor = HybridNewsExtractor(max_articles_per_source=5)
        
        # Run the pipeline
        results = await extractor.run_hybrid_pipeline(
            source_keys=sources_to_scrape,
            max_articles=max_articles_to_process
        )
        
        # Display results
        print("\n" + "="*60)
        print("EXTRACTION RESULTS SUMMARY")
        print("="*60)
        print(f"Total Articles Processed: {results.total_articles}")
        print(f"Sources: {', '.join(results.sources)}")
        print(f"Processing Time: {results.processing_timestamp}")
        
        # Display sample formatted articles
        print("\n" + "="*60)
        print("SAMPLE FORMATTED ARTICLES")
        print("="*60)
        
        for i, article in enumerate(results.articles[:3]):  # Show first 3
            print(f"\n{i+1}. TITLE: {article.title}")
            print(f"   SOURCE: {article.source}")
            print(f"   CATEGORY: {article.category}")
            print(f"   SENTIMENT: {article.sentiment}")
            print(f"   AUTHOR: {article.author or 'Unknown'}")
            print(f"   URL: {article.url}")
            print(f"   SUMMARY: {article.summary}")
            print(f"   KEY POINTS:")
            for point in article.key_points:
                print(f"     • {point}")
            print(f"   CONTENT LENGTH: {len(article.content)} characters")
            print("-" * 50)
        
        # Save results to JSON file
        output_file = f"news_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results.dict(), f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
        
        return results
        
    except Exception as e:
        print(f"Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the hybrid pipeline
    asyncio.run(main())