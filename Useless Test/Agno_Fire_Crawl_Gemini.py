from agno.agent import Agent
from agno.team import Team
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
from pydantic import BaseModel, Field
from textwrap import dedent
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

# --- Pydantic Schemas for Data Flow (Unchanged) ---

class ArticleURL(BaseModel):
    """A direct URL to a specific news article."""
    url: str = Field(..., description="The full, direct URL to a news article.")

class ArticleURLList(BaseModel):
    """A list of article URLs for a given topic."""
    urls: List[ArticleURL]

class RawArticleData(BaseModel):
    """Raw, unprocessed data scraped from an article URL."""
    title: Optional[str] = Field(None, description="The raw title scraped from the page.")
    content: str = Field(..., description="The main text content scraped from the article.")
    url: str = Field(..., description="The source URL of the content.")

class FormattedArticle(BaseModel):
    """A final, structured, and formatted news article."""
    title: str = Field(..., description="The clean headline of the article.")
    full_description: str = Field(..., description="A comprehensive summary of the article (at least 200 words).")
    source: str = Field(..., description="The publisher's name (e.g., BBC, Reuters).")
    date: Optional[str] = Field(None, description="The published date in YYYY-MM-DD format.")
    url: str = Field(..., description="The final, working URL of the article.")


# --- Agent Definitions ---

# Define a consistent parser model to handle JSON formatting
parser_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")
groq_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")


# Agent 1 (NEW): Crawls a news site for the latest article URLs
NewsCrawler = Agent(
    name="NewsCrawler",
    tools=[Crawl4aiTools()],
    model=groq_model,
    response_model=ArticleURLList,
    parser_model=parser_model,
    description="Crawls a major news website to find the latest article URLs.",
    instructions=[
        "You will be asked to find recent news articles from a specific website.",
        "Your task is to use the `Crawl4aiTools` tool on the provided news source",
        "From the crawl results, identify 2-3 of the most recent, direct URLs to specific news articles.",
        "CRITICAL: The URLs you return MUST be direct links to an article, not a homepage or a category page.",
        "Return a list containing only the final article URLs.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 2 (Unchanged): Extracts raw content from a URL
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
        "If one tool fails, try the other. Return the raw data.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 3 (Unchanged): Formats the extracted content
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
        "2.  From the URL or content, identify the `source` (e.g., Reuters, Associated Press).",
        "3.  If a publication date is present in the content, extract it and format it as YYYY-MM-DD for the `date` field. If not found, leave it as null.",
        "4.  Write a comprehensive `full_description` by summarizing the key points from the raw content. This summary must be at least 200 words.",
        "5.  Ensure the original `url` is included in the final object.",
        "CRITICAL: Do not write any explanation or introductory text. Your response must be ONLY the final JSON object that conforms to the `FormattedArticle` schema.",
    ],
    debug_mode=True,
)

# --- Team Definition (Updated) ---

NewsPipelineTeam = Team(
    name="NewsPipelineTeam",
    mode="coordinate",
    members=[NewsCrawler, ContentExtractor, ArticleFormatter], # Updated members
    model=groq_model,
    instructions=dedent("""
        You are the coordinator of a news-gathering pipeline. Your goal is to produce a fully formatted news article.

        Follow this sequence strictly:
        1.  **Delegate to `NewsCrawler`**: Get a list of recent article URLs from a major news website.
        2.  **Process the first URL**:
            a. Take the first URL from the list.
            b. **Delegate to `ContentExtractor`**: Pass this single URL to get the raw article data.
            c. **Delegate to `ArticleFormatter`**: Pass the raw data to get the final, formatted article.
        3.  **Return the Result**: Return the single `FormattedArticle` object as the final output.
    """).strip(),
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)


# --- Execution (Updated for new workflow) ---
if __name__ == "__main__":
    # Step 1: Crawl for recent news URLs
    print("--- 1. Running NewsCrawler ---")
    # We ask it to crawl a specific, reliable news source
    url_response = NewsCrawler.run("Crawl reuters.com for the 2 most recent news articles.")

    if not (url_response and url_response.content and isinstance(url_response.content, ArticleURLList) and url_response.content.urls):
        print("Failed to get URLs from crawler or URL list is empty. Exiting.")
        exit()

    print("\n>>> Output of NewsCrawler (URLs found):")
    print(url_response.content)

    # Step 2: Run ContentExtractor on the first URL
    first_url = url_response.content.urls[0]
    print(f"\n--- 2. Running ContentExtractor for URL: '{first_url.url}' ---")
    content_response = ContentExtractor.run(f"Scrape the content from this URL: {first_url.url}")

    if not (content_response and content_response.content and isinstance(content_response.content, RawArticleData)):
        print("Failed to extract content. Exiting.")
        exit()

    print("\n>>> Output of ContentExtractor (provided to next step):")
    # Printing only a snippet of the content to keep the output clean
    print(f"Title: {content_response.content.title}")
    print(f"URL: {content_response.content.url}")
    print(f"Content (first 200 chars): {content_response.content.content[:200]}...")


    # Step 3: Run ArticleFormatter
    raw_data_for_formatter = content_response.content
    print(f"\n--- 3. Running ArticleFormatter ---")
    
    # Correctly run the agent with the raw data
    formatted_article_response = ArticleFormatter.run(raw_data_for_formatter)

    print("\n>>> FINAL OUTPUT: Formatted Article <<<")
    if formatted_article_response and formatted_article_response.content:
        # The .model_dump_json() method is available on pydantic models for clean printing
        print(formatted_article_response.content.model_dump_json(indent=4))
    else:
        print("Failed to format the article.")