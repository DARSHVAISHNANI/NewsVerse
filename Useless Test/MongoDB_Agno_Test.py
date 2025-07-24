from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow
from agno.storage.mongodb import MongoDbStorage  # 👈 import your custom tool

# MongoDB connection settings
db_url = "mongodb://localhost:27017"

news_agent = Agent(
    name="News Extraction Agent",
    model=Gemini(id="gemini-2.5-flash", api_key="AIzaSyA68eFPXIGKSYjTTnvFYLltrxpKHm9BZlg"),
    description="""
        A smart AI agent designed to extract and enrich the latest verified news articles from the web.

        This agent performs the following tasks:
        1. Uses DuckDuckGo to search and retrieve links to the most recent and reputable news articles.
        2. For each article URL, it calls a custom content extraction tool (powered by Newspaper3k) to fetch the full article text, title, and publication date.
        3. Outputs a structured JSON array where each item contains:
        - headline (article title)
        - full_description (complete article body text)
        - date and time (from metadata or current timestamp)
        - source (domain name of the news site)
        - category (based on context or inferred)
        - url (original link)

        This agent is optimized for use in multi-agent AI pipelines, content intelligence systems, and real-time news monitoring dashboards.
        """,
   instructions="""
        1. Search for the 5 latest verified news articles from trusted and reputable sources using the DuckDuckGo search tool.

        2. For each resulting article URL:
        - Use the `newspaper_extractor` tool to extract the full article text, title, and publish date.
        - If publish date is not available, use the current date and time.
        - Extract the source by parsing the domain name from the URL.
        - Infer the category from the article content (e.g., Politics, Technology, Finance, Sports, etc.), or leave it empty if unclear.

        3. Return a valid JSON array containing exactly 5 news objects.
        Each object must include the following fields:
        - "headline" (from the article title)
        - "full_description" (full article body)
        - "date" (YYYY-MM-DD)
        - "time" (HH:MM format, 24-hour)
        - "source" (domain name)
        - "category" (if available)
        - "url" (original article link)

        4. Do not include explanations, notes, or Markdown in the output. Return only a pure JSON array.

        Make sure all content is factual, current, and from credible sources.
        """,
    tools=[
        DuckDuckGoTools()
    ],
    markdown=False,
    debug_mode=False,
    show_tool_calls=False,
    # storage=MongoDbStorage(collection_name="NewsData", db_url=db_url, db_name="News_Result"),
    add_history_to_messages=True
)

news_agent.print_response("""
Extract 5 latest trusted news articles using DuckDuckGo. For each article:
1. Use the URL to call `newspaper_extractor` tool.
2. Extract full article text and publish date.
3. Build a JSON with:
   - headline (from article title)
   - full_description (full article text)
   - date and time (from publish_date or today’s date)
   - source (extracted from the domain name of the URL)
   - category (guess based on article topic)
   - url

Return a clean JSON array of all 5 articles.
""")