from agno.agent import Agent
from agno.tools.website import WebsiteTools
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Define the web scraping agent
WebsiteScraperAgent = Agent(
    name="WebsiteScraper",
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    tools=[WebsiteTools()],
    description="You are a web content extractor that uses WebsiteTool to scrape a given URL.",
    instructions=[
        "Use WebsiteTool to visit the provided URL.",
        "Extract the main content, including any headlines and article body text.",
        "Do not summarize, just return the raw content found on the page.",
        "If content is minimal or missing, return a note indicating it."
    ],
    markdown=True,
    show_tool_calls=True
)

# Test with a sample news article URL
WebsiteScraperAgent.print_response("Scrape content from \"https://www.ndtv.com/india-news/2006-mumbai-local-train-blasts-bombay-high-court-acquits-12-after-19-years-8914345\"", markdown=True)
