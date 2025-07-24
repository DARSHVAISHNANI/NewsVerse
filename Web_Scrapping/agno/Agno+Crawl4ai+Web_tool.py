from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.website import WebsiteTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.crawl4ai import Crawl4aiTools
from textwrap import dedent
from dotenv import load_dotenv
import json

load_dotenv()

# -----------------------------
# Agent 1: Finds latest trending article URLs
# -----------------------------
Latest_Article_Searcher = Agent(
    name="TrendingArticleFinder",
    tools=[DuckDuckGoTools()],
    model=Groq(id="qwen/qwen3-32b"),
    description="Find the most recently published, high-impact news articles.",
    instructions=[
        "Use DuckDuckGoTools to search for the most recent trending news topics.",
        "From the top 5 results, extract URLs of individual news articles (not homepages or category pages).",
        "Return a clean list of article URLs in JSON array format: [\"url1\", \"url2\", ...]",
    ],
    show_tool_calls=True
)

# -----------------------------
# Agent 2: Extracts article metadata
# -----------------------------
Article_Extract_agent = Agent(
    name="ArticleMetadataExtractor",
    model=Groq(id="qwen/qwen3-32b"),
    tools=[Crawl4aiTools()],
    description="Extracts metadata (title, date, time, source, url) from a given article URL.",
    instructions=dedent("""
        From the provided URL, extract:
        - title: Headline of the article
        - full_description: Leave this field blank (another tool will handle this)
        - source: Publisher or site name
        - date: YYYY-MM-DD
        - time: HH:MM (24-hour format if available)
        - url: The full URL of the article
        Return this in JSON.
    """).strip(),
    markdown=True,
    show_tool_calls=True
)

# -----------------------------
# WebsiteTool for article body (used directly)
# -----------------------------
website_tool = WebsiteTools()

# -----------------------------
# Combined Pipeline
# -----------------------------
def run_full_pipeline():
    url_response = Latest_Article_Searcher.run("Find trending news article URLs.")
    print("\n🔍 Raw URL Agent Output:\n", url_response.content)

    try:
        urls = json.loads(url_response.content)
        assert isinstance(urls, list)
    except Exception as e:
        print("❌ Failed to parse URL list:", e)
        return

    print("\n🧾 Extracted URLs:", urls)

    results = []
    for url in urls:
        print(f"\n📎 Processing: {url}")
        meta_raw = Article_Extract_agent.run(f"Extract metadata from this article: {url}")
        print("📦 Metadata Agent Response:", meta_raw)

        try:
            metadata = json.loads(meta_raw) if isinstance(meta_raw, str) and meta_raw.strip().startswith("{") else {}
        except Exception as e:
            print("❌ Failed to parse metadata JSON:", e)
            continue

        metadata["url"] = metadata.get("url", url)

        # Extract body content using WebsiteTools.read_url()
        try:
            raw = website_tool.read_url(metadata["url"])
            docs = json.loads(raw)
            if docs:
                full_text = max(docs, key=lambda d: len(d.get("text", ""))).get("text", "").strip()
                metadata["full_description"] = full_text
                results.append(metadata)
            else:
                print("⚠️ No content found.")
        except Exception as e:
            print(f"❌ Failed to extract full content from {url} — {e}")

    # -----------------------------
    # Final Output
    # -----------------------------
    for idx, article in enumerate(results, 1):
        print(f"\n--- 📰 Article {idx} ---")
        print(f"- title: {article.get('title')}")
        print(f"- date: {article.get('date')}")
        print(f"- time: {article.get('time')}")
        print(f"- source: {article.get('source')}")
        print(f"- url: {article.get('url')}")
        print(f"- full_description:\n{article.get('full_description', '')[:2000]}\n")  # Truncated for readability

# Run it
run_full_pipeline()