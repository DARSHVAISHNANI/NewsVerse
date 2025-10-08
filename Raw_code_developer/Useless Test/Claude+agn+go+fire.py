from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
from textwrap import dedent
from dotenv import load_dotenv
import re

load_dotenv()

def is_valid_article_url(url, title=""):
    """
    Validate if a URL points to an individual news article, not a compilation
    """
    url_lower = url.lower()
    title_lower = title.lower()
    
    # Bad patterns that indicate news compilations
    bad_url_patterns = [
        'top-news', 'headlines', 'daily-roundup', 'news-digest',
        'summary', 'briefing', 'wrap-up', 'compilation',
        'live-updates', 'live-blog'
    ]
    
    # Bad regex patterns for category pages
    bad_regex_patterns = [
        r'/news/?$',
        r'/politics/?$', 
        r'/business/?$',
        r'index\.html?$',
        r'/category/',
        r'/section/'
    ]
    
    # Bad title patterns
    bad_title_patterns = [
        'top news', 'headlines', 'daily roundup', 'news digest',
        'live updates', 'news summary'
    ]
    
    # Check for bad patterns
    for pattern in bad_url_patterns:
        if pattern in url_lower:
            return False
    
    for pattern in bad_regex_patterns:
        if re.search(pattern, url_lower):
            return False
            
    for pattern in bad_title_patterns:
        if pattern in title_lower:
            return False
    
    # URL should be reasonably long
    if len(url) < 40:
        return False
        
    return True

# Agent 1: Find specific trending news stories
Topic_URL_Extractor = Agent(
    name="Topic_URL_Extractor",
    tools=[GoogleSearchTools()],
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    description="Finds specific trending news stories and extracts individual article URLs.",
    instructions=[
        "Use GoogleSearchTools to search for SPECIFIC trending news stories.",
        "Search for specific events like:",
        "  - 'Fed interest rate decision July 2025'",
        "  - 'Tesla earnings report July 2025'", 
        "  - 'Israel Gaza conflict July 2025'",
        "  - 'Ukraine war developments July 2025'",
        "DO NOT search for 'latest headlines', 'top stories', or 'breaking news'.",
        "",
        "Return 3-5 URLs that are individual news articles about specific stories.",
        "Each URL should focus on ONE specific event or story.",
        "Avoid URLs containing: top-news, headlines, daily-roundup, summary, briefing.",
        "Choose URLs from reliable sources: BBC, CNN, Reuters, Bloomberg, AP News.",
        "Present URLs with their story topics clearly."
    ],
    show_tool_calls=True
)

# Agent 2: Extract article content
ArticleFetcher = Agent(
    name="ArticleFetcher",
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    description="Extracts structured metadata from individual news articles.",
    tools=[FirecrawlTools()],
    instructions=dedent("""
        Extract structured metadata from news articles using FirecrawlTools.
        
        For each URL provided, extract:
        - **Title:** Article headline
        - **Description:** Full article content (minimum 500 words)
        - **Source:** Publisher name
        - **Date:** Publication date (YYYY-MM-DD format)  
        - **Time:** Publication time (HH:MM format)
        - **URL:** Article URL
        
        Focus on the main article content, ignore ads or sidebars.
        Ensure the article is about a single news story, not multiple topics.
    """),
    show_tool_calls=True
)

# Main coordinator agent
TrendingNewsCrawlerAgent = Agent(
    name="TrendingNewsCrawlerAgent",
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    team=[Topic_URL_Extractor, ArticleFetcher],
    description="Coordinates finding and extracting individual trending news stories.",
    instructions=dedent("""
        Coordinate a two-step process to find individual news stories:
        
        Step 1: Get Specific Story URLs
        - Ask Topic_URL_Extractor to search for specific trending events
        - Get 3-5 URLs for individual news articles (not compilations)
        - Each URL should be about ONE specific story
        
        Step 2: Extract Article Content  
        - Use ArticleFetcher to extract content from each validated URL
        - Get complete article metadata for each story
        
        Present results clearly with:
        - Story topic
        - Article title and description
        - Source and publication info
        - Direct URL to the story
    """),
    show_tool_calls=True,
    markdown=True
)

# Execute the agent
if __name__ == "__main__":
    try:
        print("🚀 Starting Trending News Crawler...")
        
        response = TrendingNewsCrawlerAgent.run(
            "Find 3-5 individual news stories about specific trending events today. "
            "Search for particular stories like Fed decisions, company earnings, "
            "geopolitical developments, etc. Get individual article URLs (not news compilations) "
            "and extract complete content from each story."
        )
        
        print("\n" + "="*60)
        print("INDIVIDUAL TRENDING NEWS STORIES")
        print("="*60)
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Simple fallback
        try:
            print("🔄 Trying simplified approach...")
            
            simple_agent = Agent(
                name="SimpleAgent",
                tools=[GoogleSearchTools()],
                model=Groq(id="llama-3.1-8b-instant"),
                description="Simple news finder"
            )
            
            response = simple_agent.run("Find 2 specific news article URLs about trending topics today")
            print(response.content)
            
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            print("Check your .env file and API keys.")