import os
import time
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.models.groq import Groq
from agno.team import Team
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.firecrawl import FirecrawlTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# --- Pydantic Schemas for Structured Data Flow ---

class Topic(BaseModel):
    """A single, distinct news topic."""
    topic_name: str = Field(..., description="A concise name for a trending news topic (e.g., 'Global Tech Summit 2025').")

class TopicList(BaseModel):
    """A list of trending news topics."""
    topics: List[Topic] = Field(..., description="A list of 2-3 distinct topic objects.")

class ArticleURL(BaseModel):
    """A direct URL to a specific news article."""
    url: str = Field(..., description="The full, direct URL to a news article.")

class ArticleURLList(BaseModel):
    """A list of article URLs for a given topic."""
    urls: List[ArticleURL]

class FormattedArticle(BaseModel):
    """A final, structured, and formatted news article."""
    title: str = Field(..., description="The exact headline of the article.")
    full_description: str = Field(..., description="The complete body or main content of the article, must be at least 200 words.")
    source: str = Field(..., description="The website or publication source (e.g., Bloomberg, BBC, The New York Times).")
    date: Optional[str] = Field(None, description="The publishing date in YYYY-MM-DD format, if available.")
    time: Optional[str] = Field(None, description="The publishing time in HH:MM format, if available.")
    url: str = Field(..., description="The URL of the news article.")


# --- Agent Definitions ---

# Use a powerful model for parsing structured output to ensure reliability
parser_model = Groq(id="llama3-70b-8192")

# Agent 1: Discovers trending topics
TopicDiscoverer = Agent(
    name="TopicDiscoverer",
    model=Groq(id="llama3-8b-8192"),
    response_model=TopicList,
    parser_model=parser_model,
    description="An expert web researcher who identifies 2-3 trending and relevant news topics.",
    instructions=[
        "Use GoogleSearch to search for the latest, most important trending news topics in India or globally.",
        "From the search results, extract 2-3 clear and concise topic names that best describe the current events.",
        "Focus on fresh, significant topics that people are actively reading about today.",
        "Return a list of these topic names.",
    ],
    tools=[GoogleSearchTools()],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 2: Finds a specific article URL for a given topic
URLFinder = Agent(
    name="URLFinder",
    model=Groq(id="llama3-8b-8192"),
    response_model=ArticleURLList,
    parser_model=parser_model,
    description="An expert content finder that, given a topic, finds the URL of a relevant and recent news article.",
    instructions=[
        "You will be given a single news topic.",
        "Use GoogleSearchTools to find 1-2 direct URLs to specific news articles about this topic.",
        "Prioritize well-known, reliable news sources.",
        "CRITICAL: The URLs must point to a specific article, not a homepage (e.g., 'bbc.com/news/article-123' is good, 'bbc.com' is bad).",
        "Return a list containing the article URL(s).",
    ],
    tools=[GoogleSearchTools()],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 3: Extracts and formats content from a URL
ArticleExtractor = Agent(
    name="ArticleExtractor",
    model=Groq(id="llama3-70b-8192"), 
    response_model=FormattedArticle,
    parser_model=parser_model,
    description="An expert news content extractor that scrapes a URL and formats the content.",
    instructions=dedent("""
        You will be given a single URL. You have two different web scraping tools available.
        1.  Use one of the available scraping tools to fetch the content of the page.
        2.  **CRITICAL**: If the first tool fails or returns empty content, you MUST try the other available tool.
        3.  Once content is successfully extracted, analyze it to create a structured `FormattedArticle`.
        4.  The `title` must be the exact headline of the article.
        5.  The `full_description` must be the complete main body of the article and be at least 200 words.
        6.  Identify the `source` (e.g., Bloomberg, BBC) from the URL or page content.
        7.  Find the `date` (YYYY-MM-DD) and `time` (HH:MM), if available.
        8.  If you cannot extract content after trying all tools, you must report the failure.
        9.  Return the final, structured `FormattedArticle` object.
    """).strip(),
    # Provide two different scraping tools for resilience
    tools=[FirecrawlTools()], 
    show_tool_calls=True,
    debug_mode=True,
)

# --- Main Execution Block (for Debugging and Clarity) ---
if __name__ == "__main__":
    start_time = time.time()
    
    # --- STEP 1: Find Trending Topics ---
    print("--- 1. Running TopicDiscoverer to find trending topics... ---")
    topic_response = TopicDiscoverer.run("Find 2 trending news topics today.")
    
    if not (topic_response and topic_response.content and isinstance(topic_response.content, TopicList) and topic_response.content.topics):
        print("\n❌ Failed to get topics. Exiting.")
        exit()
        
    print("\n✅ Output of TopicDiscoverer (Topics Found):")
    for i, topic in enumerate(topic_response.content.topics):
        print(f"   {i+1}. {topic.topic_name}")
    
    # --- Process Each Topic Sequentially ---
    all_formatted_articles = []
    for topic in topic_response.content.topics:
        print("\n" + "="*80)
        print(f"--- 2. Running URLFinder for topic: '{topic.topic_name}' ---")
        
        # --- STEP 2: Find URL for the Topic ---
        url_response = URLFinder.run(f"Find a recent news article URL about '{topic.topic_name}' from a major news source.")
        
        if not (url_response and url_response.content and isinstance(url_response.content, ArticleURLList) and url_response.content.urls):
            print(f"\n❌ Failed to find a URL for the topic '{topic.topic_name}'. Skipping.")
            continue
            
        first_url_obj = url_response.content.urls[0]
        print(f"\n✅ Output of URLFinder (URL Found): {first_url_obj.url}")
        
        # --- STEP 3: Extract Content from the URL ---
        print(f"\n--- 3. Running ArticleExtractor for URL: '{first_url_obj.url}' ---")
        
        # We pass the pydantic object's data to the agent
        article_response = ArticleExtractor.run(
            f"Please extract the article content from the following URL: {first_url_obj.url}"
        )
        
        if not (article_response and article_response.content and isinstance(article_response.content, FormattedArticle)):
            print(f"\n❌ Failed to extract the article from '{first_url_obj.url}'. Skipping.")
            continue
        
        print("\n✅ FINAL FORMATTED OUTPUT FOR THIS ARTICLE:")
        # The .print_response() method on an agent is great for displaying the last run's result
        ArticleExtractor.print_response(markdown=True)
        all_formatted_articles.append(article_response.content)

    print("\n" + "="*80)
    print("🚀 PIPELINE COMPLETED SUCCESSFULLY! 🚀")
    print(f"Total formatted articles generated: {len(all_formatted_articles)}")

    end_time = time.time()
    print(f"\nTotal Time Taken To Run: {end_time - start_time:.2f} seconds")