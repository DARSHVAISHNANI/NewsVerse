import os
import time
from textwrap import dedent
from typing import Optional, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()

# 1. Pydantic parser model defined for structured output
class Article(BaseModel):
    """A structured representation of a news article."""
    title: str = Field(..., description="The exact headline of the article")
    full_description: str = Field(
        ...,
        min_length=200,
        description="The complete body or main content of the article, at least 200 words long."
    )
    source: str = Field(..., description="The website or publication source (e.g., Bloomberg, BBC)")
    date: Optional[str] = Field(None, description="The publishing date in YYYY-MM-DD format.")
    time: Optional[str] = Field(None, description="The publishing time in HH:MM format.")
    url: HttpUrl = Field(..., description="The working URL of the news article.")

start_time = time.time()

# Agent to find 3 trending topics
Latest_Article_Searcher = Agent(
    name="TopicExtractor",
    model=Groq(id="qwen/qwen3-32b"),
    description="An expert web researcher who identifies trending news topics.",
    instructions=[
        "Use DuckDuckGo to search for the latest trending news.",
        "From the search results, extract **exactly 3** clear and distinct topic names.",
        "Return only the list of 3 topic names."
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
)

# Agent to find a URL for a given topic
URL_Extractor_Agent = Agent(
    name="URLFetcher",
    model=Groq(id="qwen/qwen3-32b"),
    description="An expert content finder that gets the best URL for a news topic.",
    instructions=[
        "Given a topic, use DuckDuckGo to find 3 most recent article URL from a major news source.",
        "Return only the single, direct URL of the article.",
    ],
    # 2. Corrected tool to use DuckDuckGo for searching, not Crawl4ai
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
)

pm = Groq(id="llama3-70b-8192")

# Agent to extract content from a URL
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model=Groq(id="qwen/qwen3-32b"),
    description="An expert news content extractor that uses Crawl4ai to scrape a URL and structure the data.",
    instructions="From the provided URL, use the Crawl4ai tool to extract the main article's content and structure it according to the Article model.",
    tools=[Crawl4aiTools(max_length=4000)], # Increased max_length for full articles
    # 3. Using the Pydantic model to enforce structured output
    parser_model=pm,
    references_format=Article,
    markdown=True,
    show_tool_calls=True,
)

# Combine agents into a team
agent_team = Agent(
    team=[Latest_Article_Searcher, URL_Extractor_Agent, Article_Extract_agent],
    model=Groq(id="qwen/qwen3-32b"),
    instructions=[
        "First, use TopicExtractor to get exactly 3 news topics.",
        "Then, for each topic, use URLFetcher to find atmost 3 its article URL.",
        "Finally, for each URL, use ArticleFetcher to extract the structured content.",
        "Compile the 3 structured articles for the final output."
    ],
    markdown=True,
    show_tool_calls=True,
    monitoring=True,
)

# 4. A clearer, more effective final prompt for the team
agent_team.print_response(
    "Identify exactly 3 trending news topics from today, July 31, 2025. For each topic, find a "
    "corresponding article URL and extract its content into a structured format. "
    "Return the final output as a list of 3 structured news articles.",
    stream=True
)

end_time = time.time()

print(f"\nTotal Time Taken To Run: {end_time - start_time:.2f} seconds")