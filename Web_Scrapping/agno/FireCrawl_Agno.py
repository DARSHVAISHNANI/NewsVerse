from agno.agent import Agent
from textwrap import dedent
from agno.models.google import Gemini
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv
load_dotenv()

#Create a agent that can extract latest news topic on which article url can be crawl
Latest_Article_Searcher = Agent(
    name="TopicExtractor",
    model=Gemini(id="gemini-2.0-flash"),
    description="Your an expert article searcher who can find best and latest topic for news extraction.",
    instructions=[""
        "Use DuckDuckGo to search for articles Topics.",
        "Provide the article topic name to URLFetcher."],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)


#Create a agent that can extract latest news article url
URL_Extractor_Agent = Agent(
    name="URLFetcher",
    model = Gemini(id="gemini-2.0-flash"),
    description="You are an expert content finder. Your task is to find the URL of the latest article on any topic but must be latest.",
    instructions= [
         "Use DuckDuckGo to search for articles.",
        "Return the URL of the article with the latest publication date.",
        "If no publication date is found, use the first valid article."
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

# Using Firecrawl api, extract the contain of each url that is extracted by ArticleFetcher will give taken by firecrawl.
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model= Gemini(id="gemini-2.0-flash"),
    description= "You are an expert news content extractor.",
    instructions= dedent("""
        You are an expert news content extractor.

        From the provided URL, extract **only the latest news article** in the following structured format:

        - title: The exact headline of the article
        - full_description: The complete body or main content of the article
        - source: The website or publication source (e.g., Reuters, BBC)
        - date: The publishing date (in format YYYY-MM-DD if available)
        - time: The publishing time (in HH:MM format if available)
        - url: The URL of the news article

        If multiple articles are on the page, extract only the most recent or top one. Be precise and concise.
    """).strip(),
    tools=[FirecrawlTools(scrape=True, crawl=True)],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

#Combine this both ai agent to create a team
agent_team = Agent(
    team=[Latest_Article_Searcher, URL_Extractor_Agent, Article_Extract_agent],
    model=Gemini(id="gemini-2.0-flash"),
    instructions=["First execute the url from the URL_Extractor_Agent and then take each url and Extract or web scrape the article content of each url in a structured format like title, full_description, source, date, time, and paste the url from the agent."],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

agent_team.print_response("Extract 3 latest news article url from well know news websites", stream=True)