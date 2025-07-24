from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
from textwrap import dedent
from dotenv import load_dotenv

load_dotenv()

# Agent 1: Topic_URL_Extractor (find trending news topics and URLs)
Topic_URL_Extractor = Agent(
    name="Topic_URL_Extractor",
    tools=[GoogleSearchTools()],
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    description="Identifies trending news topics and retrieves structured article URLs from reliable news sources.",
    instructions=[
        "Use search queries like 'latest headlines July 21 2025', 'top stories today', 'breaking news July 21 2025', etc.",
        "Return 3–5 distinct URLs from this sources sucj as BBC, CNN, Benzinga, Bloomberg, Times of India related to trending topics.",
        "Each URL must link directly to a full news article — not a homepage, index, or video page.",
        "Examples of valid structures include:",
        "  - https://www.bbc.com/news/articles/c23g5xpggzmo",
        "  - https://edition.cnn.com/2025/07/18/middleeast/israel-syria-ceasefire-latam-intl",
        "  - https://www.benzinga.com/markets/macro-economic-events/25/07/46491573/waller-fed-chair-trump-rate-cut-july",
        "Avoid URLs with `.html` endings or that redirect. Use clean, article-specific links.",
        "Also avoid using youtube links."
    ],
    show_tool_calls=True,
    debug_mode=True
)

# Step 2: Agent to extract article metadata from a given URL
ArticleFetcher = Agent(
    name="ArticleFetcher",
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    description="You are an expert article fetecher who has a task to extracts structured metadata from a news article using FireCrawl scraping tools.",
    instructions=dedent("""
        Given a news article URL, extract its content in the following format:

        - title: The headline of the article.
        - full_description: A full summary or body of the article (at least 500 words).
        - source: The publisher's name (e.g., BBC, CNN, Reuters).
        - date: The published date in YYYY-MM-DD format.
          If not found in metadata, look for text like "Published on July 21, 2025".
        - time: The time in HH:MM format.
          Extract from metadata or phrases like "8:34 AM", "15:47", etc.
        - url: The final working URL of the article.
          If the original is broken, fallback to a working or cached version.

        If multiple articles appear, choose the most recent and relevant one.
        Be precise — use metadata and semantic patterns where needed.
    """).strip(),
    tools=[FirecrawlTools()],  # ✅ No `scrape=True` needed here
    markdown=True,
    show_tool_calls=True
)

# Combined Meta-Agent
TrendingNewsCrawlerAgent = Agent(
    name="TrendingNewsCrawlerAgent",
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    team=[Topic_URL_Extractor, ArticleFetcher],
    description="An intelligent agent that finds today's trending news articles and extracts structured metadata from them using search and web crawling tools.",
    instructions=dedent("""
        Step 1: Use Topic_URL_Extractor to identify trending news topics that people are reading today and Extract the url of the article from the well know websites. example for trending topics are "the air india plane crash", "war between Iran and Iserali".
        Step 2: Make sure the article that you choose must be single topic article means that article should only contain news related to that topic.
        Step 3: Now using the extracted URL use each URL one by one.
        Step 3: For each URL, use FirecrawlTools to extract structured article content including:
            - title
            - full_description (at least 500 words)
            - source
            - date
            - time
            - url

        Return the final output as a list of structured news articles.
    """).strip(),
    show_tool_calls=True,
    markdown=True
)

# Trigger Agent Execution
TrendingNewsCrawlerAgent.print_response(
    "Step 1: Use Topic_URL_Extractor to identify trending news topic's URL that people are reading today.\n"
    "Step 2: For each URL, use FireCrawler to extract structured article content including:\n"
    "- title\n- full_description at least 500 words long\n- source\n- date\n- time\n- url\n\n"
    "Return the final output as a list of structured news articles.",
    markdown=True
)