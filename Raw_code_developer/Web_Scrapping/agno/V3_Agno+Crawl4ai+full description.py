from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.models.groq import Groq
from textwrap import dedent
from dotenv import load_dotenv

load_dotenv()

# Agent 1: Finds latest trending article URLs
Latest_Article_Searcher = Agent(
    name="TrendingArticleFinder",
    tools=[DuckDuckGoTools()],
    model=Groq(id="qwen/qwen3-32b"),
    description="You're a professional web scout trained to identify the most recently published, high-impact news articles. "
                "You search for trending news and return direct URLs to recent, reputable articles.",
    instructions=[
        "Use DuckDuckGoTools to search for the most recent trending news topics.",
        "From the top 5 search results, extract direct URLs pointing to individual news articles (not homepages or indexes).",
        "Return only valid article URLs. No placeholders, redirects, or template pages.",
        "Avoid URLs ending in .html. Prefer modern article paths with date slugs.",
        "Return a clean list of article URLs only — no summaries or duplicates."
    ],
    show_tool_calls=True
)

# Agent 2: Extracts structured article content
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model=Groq(id="qwen/qwen3-32b"),
    description="You are an expert news content extractor.",
    instructions=dedent("""
        You are an expert news content extractor.

        From the provided URL, extract only the latest news article in the following structured format:

        - title: The article's headline
        - full_description: Leave this field blank — another agent will provide the content
        - source: Website or publisher (e.g., BBC, Reuters)
        - date: Publishing date in YYYY-MM-DD format
        - time: Publishing time in HH:MM format (if available)
        - url: The exact URL of the article

        Use metadata first. If missing, scan for publish labels like 'Published on July 18, 2025 at 9:20 AM'.
        Return only one structured article from the page.
    """).strip(),
    tools=[Crawl4aiTools()],
    markdown=True,
    show_tool_calls=True
)

# Agent 3: Extracts 500-word article body
LongDescriptionAgent = Agent(
    name="LongDescriptionExtractor",
    model=Groq(id="qwen/qwen3-32b"),
    description="You are a content-focused extractor who retrieves the full article body (approx. 500 words).",
    instructions=dedent("""
        From the provided article URL, extract only the main body of the article.

        - Output approximately 500 words of readable, coherent content.
        - Focus on the core news content — exclude ads, navigation, footers, etc.
        - Use pattern recognition or metadata hints to target the article body.
        - If the article is shorter than 500 words, return as-is without padding.

        Return only the raw article body (no HTML, metadata, or summaries).
    """).strip(),
    tools=[Crawl4aiTools()],
    markdown=True,
    show_tool_calls=True
)

# Team that orchestrates all agents
agent_team = Agent(
    team=[Latest_Article_Searcher, Article_Extract_agent, LongDescriptionAgent],
    model=Groq(id="qwen/qwen3-32b"),
    instructions=[
        "Step 1: Ask TrendingArticleFinder to fetch a list of trending article URLs.",
        "Step 2: For each URL, ask ArticleFetcher to extract metadata (title, date, time, source, url).",
        "Step 3: Ask LongDescriptionExtractor to extract a 500-word body from the same URL.",
        "Step 4: Combine metadata with the body into a structured object with fields: title, full_description, source, date, time, url.",
        "Ensure that full_description has approximately 500 words, taken from the article’s main body.",
        "Return the list of these complete article objects."
    ],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

# Execute the full workflow
agent_team.print_response(
    "Find trending article URLs and return structured news data including title, date, time, source, url, and 500-word full_description.",
    markdown=True
)