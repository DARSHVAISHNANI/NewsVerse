from agno.agent import Agent
from agno.team import Team
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.groq import Groq
from pydantic import BaseModel, Field
from textwrap import dedent
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

# --- Pydantic Schemas for Data Flow ---

class Topic(BaseModel):
    """A single, distinct news topic."""
    topic_name: str = Field(..., description="A concise name for a trending news topic (e.g., 'Global Tech Summit 2025').")

class TopicList(BaseModel):
    """A list of trending news topics."""
    topics: List[Topic] = Field(..., description="list of topic objects extracted.")

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
    source: str = Field(..., description="The publisher's name (e.g., BBC, CNN).")
    date: Optional[str] = Field(None, description="The published date in YYYY-MM-DD format.")
    url: str = Field(..., description="The final, working URL of the article.")


# --- Agent Definitions ---

# Define a consistent parser model to handle JSON formatting
parser_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")
groq_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")

# Agent 1: Discovers trending topics
TopicDiscoverer = Agent(
    name="TopicDiscoverer",
    tools=[DuckDuckGoTools()],
    model=groq_model,
    response_model=TopicList,
    parser_model=parser_model, # Use a parser to handle the structured output
    description="Identifies 2-3 current and trending news topics from around the world.",
    instructions=[
        "Use the search tool to find today's top news headlines or trending topics.",
        "Identify 2-3 distinct, high-level topics (e.g., 'International Climate Conference', 'AI Regulation Developments').",
        "Then, provide the list of topics you found.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 2: Finds URLs for a given topic
URLFinder = Agent(
    name="URLFinder",
    tools=[DuckDuckGoTools()],
    model=groq_model,
    response_model=ArticleURLList,
    parser_model=parser_model,
    description=(
        "An expert web researcher who, given a specific news topic, specializes in finding the most relevant and reliable article URLs. "
        "Your job is to meticulously search the web to pinpoint direct links to high-quality news sources for further processing."
    ),
    instructions=[
        "You will be given a single news topic.",
        "Your task is to use the DuckDuckGo search tool to find 1-2 of the best article URLs that directly report on this topic.",
        "From your search results, select the URLs that are most relevant, recent, and authoritative.",
        "CRITICAL: The URLs you return MUST be direct links to a specific article, not a news homepage or a category page. For example, 'cnn.com/world/some-article-title' is correct, but 'cnn.com' or 'cnn.com/world' are incorrect.",
        "Prioritize well-known, any reputable news publishers who's website is accessible.",
        "Return a list containing only the final, validated article URLs.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

# Agent 3: Extracts raw content from a URL
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

# Agent 4: Formats the extracted content
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
        "2.  From the URL or content, identify the `source` (e.g., Boston.com, BBC).",
        "3.  If a publication date is present in the content, extract it and format it as YYYY-MM-DD for the `date` field. If not found, leave it as null.",
        "4.  Write a comprehensive `full_description` by summarizing the key points from the raw content. This summary must be at least 200 words.",
        "5.  Ensure the original `url` is included in the final object.",
        "CRITICAL: Do not write any explanation or introductory text. Your response must be ONLY the final JSON object that conforms to the `FormattedArticle` schema.",
    ],
    debug_mode=True,
)

# --- Team Definition ---

NewsPipelineTeam = Team(
    name="NewsPipelineTeam",
    mode="coordinate",
    members=[TopicDiscoverer, URLFinder, ContentExtractor, ArticleFormatter],
    model=groq_model,
    instructions=dedent("""
        You are the coordinator of a news-gathering pipeline. Your goal is to produce a list of fully formatted news articles.

        **Follow this sequence strictly and sequentially. Do not perform steps in parallel.**

        1.  **Delegate to `TopicDiscoverer`**: Get a list of 2 trending topics.
        2.  **Process ONE topic at a time**:
            a. Take the first topic from the list.
            b. **Delegate to `URLFinder`**: Pass this single topic to get 1-2 article URLs.
            c. Take the first URL from that list.
            d. **Delegate to `ContentExtractor`**: Pass this single URL to get the raw article data.
            e. **Delegate to `ArticleFormatter`**: Pass the raw data to get the final, formatted article.
        3.  **Aggregate and Return**: Collect the `FormattedArticle` object into a list and return it as the final output. For now, only process the first topic and first article to ensure the pipeline works.
    """).strip(),
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

# --- Execution (Showing Intermediate Outputs) ---
if __name__ == "__main__":
    # Step 1: Run TopicDiscoverer
    print("--- 1. Running TopicDiscoverer ---")
    topic_response = TopicDiscoverer.run("Find the top 2 trending news topics in the world right now.")
    
    if not (topic_response and topic_response.content and isinstance(topic_response.content, TopicList) and topic_response.content.topics):
        print("Failed to get topics or topic list is empty. Exiting.")
        exit()
        
    print("\n>>> Output of TopicDiscoverer (provided to next step):")
    print(topic_response.content)
    
    # Step 2: Run URLFinder
    first_topic = topic_response.content.topics[0]
    print(f"\n--- 2. Running URLFinder for topic: '{first_topic.topic_name}' ---")
    url_response = URLFinder.run(f"Find 2 article URLs about '{first_topic.topic_name}'.")

    if not (url_response and url_response.content and isinstance(url_response.content, ArticleURLList) and url_response.content.urls):
        print("Failed to get URLs or URL list is empty. Exiting.")
        exit()

    print("\n>>> Output of URLFinder (provided to next step):")
    print(url_response.content)

    # Step 3: Run ContentExtractor
    first_url = url_response.content.urls[0]
    print(f"\n--- 3. Running ContentExtractor for URL: '{first_url.url}' ---")
    content_response = ContentExtractor.run(f"Scrape the content from this URL: {first_url.url}")

    if not (content_response and content_response.content and isinstance(content_response.content, RawArticleData)):
        print("Failed to extract content. Exiting.")
        exit()

    print("\n>>> Output of ContentExtractor (provided to next step):")
    # Printing only a snippet of the content to keep the output clean
    print(f"Title: {content_response.content.title}")
    print(f"URL: {content_response.content.url}")
    print(f"Content (first 200 chars): {content_response.content.content[:200]}...")


    # Step 4: Run ArticleFormatter
    raw_data_for_formatter = content_response.content
    print(f"\n--- 4. Running ArticleFormatter ---")
    
    # Correctly run the agent with the raw data
    formatted_article_response = ArticleFormatter.run(raw_data_for_formatter)

    print("\n>>> FINAL OUTPUT: Formatted Article <<<")
    if formatted_article_response and formatted_article_response.content:
        # The .pretty() method is available on pydantic models for clean printing
        print(formatted_article_response.content.model_dump_json(indent=4))
    else:
        print("Failed to format the article.")





