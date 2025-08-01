from agno.agent import Agent
from textwrap import dedent
from agno.models.google import Gemini
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv
load_dotenv()

# Agent 1: Finds topics AND their URLs in a single search.
Topic_and_URL_Searcher = Agent(
    name="TopicAndUrlSearcher",
    model=Gemini(id="gemini-2.0-flash"),
    description=(
        "You are an efficient news scout. Your primary function is to perform a SINGLE web search to find "
        "three distinct, trending news topics and their corresponding direct article URLs from reputable sources."
    ),
    instructions=[
        "This entire task must be completed with only ONE call to the DuckDuckGo tool.",
        "Perform a single search for 'top news stories today' or 'trending international news'.",
        "From that one search result, identify 3 distinct news articles from reputable sources (e.g., Reuters, BBC, Associated Press).",
        "For each article, you must return its main topic and its direct URL.",
        "Output ONLY a list of the topics and their corresponding URLs."
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)


# Agent 2: Scrapes a URL and extracts structured data. (This agent is unchanged)
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model=Gemini(id="gemini-2.0-flash"),
    description="You are a data extraction specialist. Your task is to receive a news article URL and use the Firecrawl tool to scrape its content, structuring it into a precise format.",
    instructions=dedent("""
        You will be given a single URL.
        1. Use the Firecrawl tool to scrape the full content of the provided URL.
        2. From the scraped data, extract the following details for the main news article.
        3. Structure your final output precisely as follows:

        - title: The exact headline of the article.
        - full_description: The complete body of the article. Ensure it is detailed and comprehensive.
        - source: The name of the publication (e.g., Reuters, BBC News).
        - date: The publishing date in YYYY-MM-DD format.
        - time: The publishing time in HH:MM format (if available).
        - url: The original URL you were given.

        Ensure all fields are accurately filled. Be precise and concise.
    """).strip(),
    tools=[FirecrawlTools(scrape=True, crawl=False)],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

# The orchestrator agent team, now with only two agents.
agent_team = Agent(
    team=[Topic_and_URL_Searcher, Article_Extract_agent], # The URL_Extractor_Agent has been removed.
    model=Gemini(id="gemini-2.0-flash"),
    instructions=[
        "Your mission is to generate a report of recent news articles.",
        "First, use the TopicAndUrlSearcher to perform a single search to get three topics and their URLs.",
        "Then, for each URL returned, use the ArticleFetcher to scrape and structure the article's content.",
        "Compile the final structured articles as your output."
    ],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

# The final prompt remains the same as it correctly describes the overall goal.
agent_team.print_response(
    "Find three trending news topics from today, and for each one, "
    "extract the full article content from a reputable news source. "
    "Present the final result as a list of structured articles.",
    stream=True
)