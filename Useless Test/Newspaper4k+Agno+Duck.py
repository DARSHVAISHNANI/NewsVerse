import os
import time
from textwrap import dedent
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()

# Define the data structure for the output using Pydantic
class Article(BaseModel):
    """A structured representation of a news article."""
    title: str = Field(..., description="The exact headline of the article")
    full_description: str = Field(
        ...,
        min_length=200,
        description="The complete body or main content of the article, at least 200 words long."
    )
    source: str = Field(..., description="The website or publication source (e.g., Bloomberg, BBC, The New York Times)")
    date: Optional[str] = Field(None, description="The publishing date in YYYY-MM-DD format.")
    time: Optional[str] = Field(None, description="The publishing time in HH:MM format.")
    url: HttpUrl = Field(..., description="The URL of the news article.")

start_time = time.time()

# Agent to find trending topics
Latest_Article_Searcher = Agent(
    name="TopicExtractor",
    model=Gemini(id="gemini-1.5-flash"),
    description=(
        "You're an expert web researcher who specializes in identifying the most trending and relevant news topics."
    ),
    instructions=[
        "Use DuckDuckgo to search for the latest trending news articles.",
        "From the top 5 search results, extract clear and concise topic names.",
        "Return only the topic name (not the URL or summary).",
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
    debug_mode=True  # 🐛 Turn on debugging
)

# Agent to find a URL for a given topic
URL_Extractor_Agent = Agent(
    name="URLFetcher",
    model=Gemini(id="gemini-1.5-flash"),
    description="You are an expert content finder. Your task is to find 3 URL of the latest article on any given topic.",
    instructions=[
        "Use the DuckDuckgo tool to search for articles on the given topic.",
        "Return the URL of the article with the latest publication date.",
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
    debug_mode=True  # 🐛 Turn on debugging
)

# Agent to extract article content
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model=Groq(id="qwen/qwen3-32b"),
    description="You are an expert news content extractor that takes a URL and returns structured data based on the Article model.",
    instructions="From the provided URL, extract the content of the most prominent news article using the Newspaper4k tool.",
    tools=[Newspaper4kTools()],
    reasoning=True,
    markdown=True,
    show_tool_calls=True,
    debug_mode=True  # 🐛 Turn on debugging
)

# Combine the agents into a team
agent_team = Agent(
    team=[Latest_Article_Searcher, URL_Extractor_Agent, Article_Extract_agent],
    model=Groq(id="qwen/qwen3-32b"),
    instructions=[
        "First, get 3 trending news topics using TopicExtractor.",
        "Then, for each topic, find the most recent article URL using URLFetcher.",
        "Finally, for each URL, extract the article content using ArticleFetcher."
    ],
    markdown=True,
    show_tool_calls=True,
    monitoring=True,
    debug_mode=True  # 🐛 Turn on debugging for the orchestrator
)

# Execute the agent team with your original prompt
agent_team.print_response(
    "Step 1: Use TopicExtractor to identify 3 trending news topics of todays.\n"
    "Step 2: For each topic, use URLFetcher to find the most recent article URL from a well-known news site.\n"
    "Step 3: For each URL, use ArticleFetcher to extract structured article content.",
    stream=True
)

end_time = time.time()

print(f"\nTotal Time Taken To Run: {end_time - start_time:.2f} seconds")